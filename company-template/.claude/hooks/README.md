# The guard

`.claude/hooks/guard.py` turns one rule in `READ-FIRST.md` into code: nothing
leaves this folder unless you approved a card for it, and your approval has to
be something you typed. Claude Code runs the guard before every tool call, and
the guard can stop the call.

`.claude/settings.json` registers it on two events:

- `PreToolUse`, for every tool. The hook reads the event as JSON on standard
  input. Exit code 0 lets the call go on through the normal permission flow.
  Exit code 2 blocks the call, and what the guard printed is shown to the
  model as the reason.
- `UserPromptSubmit`, run as `guard.py --prompt`. The hook reads the text you
  typed from the event's `prompt` field. It never blocks a prompt: it always
  exits 0 and prints at most one short line telling you which card numbers it
  recorded.

## How an approval works now

1. The agent shows a card and adds it to `log/cards.md`, then stops.
2. You type `yes C-<n>` in the chat.
3. The prompt hook sees your typed text and appends one line to the approvals
   log in this folder's `.claude/` folder: the time, `yes C-<n>`, and
   `typed by owner`.
4. The agent retries the call. The guard allows it only if a card in
   `log/cards.md` names this tool AND that card has an unspent yes in the
   approvals log.
5. When the guard allows the call, it spends the yes: it appends a `used`
   line for that card number and the tool name. The next outbound call needs
   a new typed yes.

Two things follow from this:

- **A `yes` written into `log/cards.md` approves nothing.** The agent can
  write that file, so the guard stopped trusting it. Only the approvals log
  counts, and the only thing that writes a yes line there is the prompt hook,
  reading text you typed.
- **One yes, one action.** The guard spends the approval itself, so it no
  longer depends on the agent posting `done C-<n>`. Post the readback anyway,
  for you: it is the record of what actually happened.

Only `yes C-<n>` counts. `ok`, `looks good`, a thumbs up, `yes` on its own and
`yes to everything` record nothing. Several explicit numbers in one message
(`yes C-4 yes C-5`) each get recorded. If several approved cards match one
call, the guard spends the lowest number.

## The guard's own files

The agent may read these and never write, move or delete them:

- the approvals log in the `.claude/` folder
- `.claude/hooks/` and everything inside it
- `.claude/settings.json` and a local settings file beside it
- `.claude/guard-allow.txt`

These blocks apply always, with any card, and the allow file does not waive
them. They cover `Write`, `Edit`, `MultiEdit` and `NotebookEdit`, and shell
commands that name one of these paths as something to change: a `>` or `>>`
redirection, `tee`, `cp`, `mv`, `rm`, `sed -i`, `truncate` and similar. You
edit these files by hand.

## What it blocks, whatever the cards say

This is the never list from `READ-FIRST.md`:

- a shell delete that touches anything outside `output/`, including
  `rm`, `rmdir`, `shred`, `truncate`, `git clean`, `git reset`, `git rm`,
  and a `find` that deletes or runs a command;
- anything that looks like a bulk send or a campaign;
- any outbound call that names more than 3 people at once.

No card approves these. The owner does them by hand.

## What it always allows

- reading, searching and listing: `Read`, `Grep`, `Glob`, `LS`, and the web
  fetch and web search tools, including reading the guard's own files;
- writing inside this folder: `Write` and `Edit` to a path under the company
  folder, which is where drafts belong;
- shell commands that are plainly local, such as `ls`, `cat`, `grep`, `git
  status`, `git commit`, and a plain `curl` that only reads a page;
- MCP tool calls whose name reads like a read: `get`, `list`, `search`,
  `read`, `fetch`, `find`, and similar.

## What needs a card and a typed yes

Outbound means one of these:

- an MCP tool whose name reads like a write: `send`, `reply`, `create`,
  `update`, `delete`, `post`, `publish`, `schedule`, `book`, `pay`,
  `invite`, `share`, `upload`, `comment`, `merge`, and similar;
- a shell command that sends data out: `curl` or `wget` with a body or a
  POST, PUT, PATCH or DELETE method, `mail`, `sendmail`, `msmtp`,
  `git push`, `gh` with a writing subcommand, `scp` or `rsync` to a remote
  host, `ssh`.

The matching rule: both the card's `tool:` field and the tool name (or, for a
shell command, its first word) are lowercased, split at camel case, and every
other character becomes a space. They match when either string contains the
other, or when every word of the card's tool field, each at least three
characters, also appears in the tool name. A card with an empty tool field or
`by hand` never matches a tool call.

So a card written as `tool: mailbox send message` approves a call to
`mcp__mailbox__send_message`, once you have typed the yes for that card. A
card for a different tool, or a yes for a different card number, does not.

## Unknown tools

A tool the guard has never heard of is blocked. That is on purpose: a new
send-capable tool should not slip through because nobody wrote a rule for it.

## How to test it

```bash
python3 .claude/hooks/guard.py --self-test
```

That runs about twenty-five built-in cases against a temporary folder and
prints one PASS or FAIL line each. Exit code 0 only when all of them pass.

To try one call by hand, feed the guard an event on standard input:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git push"},"cwd":"'"$PWD"'"}' \
  | python3 .claude/hooks/guard.py; echo "exit $?"
```

And one typed yes:

```bash
echo '{"hook_event_name":"UserPromptSubmit","prompt":"yes C-1","cwd":"'"$PWD"'"}' \
  | python3 .claude/hooks/guard.py --prompt; echo "exit $?"
```

## How to allow one more read-only tool

Add its name to `.claude/guard-allow.txt`, one pattern per line, `*` allowed,
`#` for comments. That file is for tools that only read. For a bigger change,
such as a new local shell command, edit the lists at the top of
`.claude/hooks/guard.py`: `WRITE_VERBS`, `READ_VERBS`, `SAFE_SHELL`,
`OUTBOUND_SHELL`, `EXTRA_ALLOWED_TOOLS`, `RECIPIENT_KEYS`, `BULK_WORDS` and
`MAX_RECIPIENTS`. Both files are on the protected list, so you edit them
yourself.

## Limits, honestly

- It runs in Claude Code only. Another agent reading this folder gets no
  guard from this file and needs its own permission settings.
- It is pattern matching on tool names and command text. It will be wrong in
  both directions: it will block a harmless command it does not recognise,
  and a tool with a bland name that sends mail can read as a safe call.
- It reads the event Claude Code gives it. A command that builds itself at
  runtime, or a script the agent writes to disk and then runs through an
  allowed interpreter, is not inspected. The self protection covers paths
  named in a shell command; it does not read inside a program, so an inline
  `python -c` or a script file that writes a protected path is out of scope.
- The prompt hook fires on prompts you type, and Claude Code also fires it on
  a few turns it starts itself, such as a scheduled task or a background
  agent reporting back. Text arriving that way is treated like typed text.
- The guard spends the yes when it allows the call, which is before the tool
  actually runs. If the call then fails, or you deny it at the permission
  prompt, the yes is gone and you type a new one.
- An agent with unrestricted shell access on a machine can still find ways
  around a hook. Keep send-capable credentials away from agents that do not
  need them. A tool that cannot send cannot send by accident.
