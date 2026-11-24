# company-in-a-folder

**An AI operating system for a whole business. 83 jobs across 13 departments, one company folder they all read, and a guard that stops anything leaving without your typed yes.**

Most skill packs give your AI a method and no memory of your company. Most company-folder templates give it a memory and nothing to do. This is both: the folder holds what is true about your business, and every job reads it before it writes a word.

Plain text files and a few small Python scripts. Works with Claude Code, Codex, Cursor and any agent that reads `AGENTS.md`. MIT licensed. No account, no signup, no paid tool needed.

## Try it in two minutes

You do not have to fill anything in. The kit ships a complete made-up company, Tidewater Sign & Print, with a real Monday waiting for it: 14 emails, a clashing calendar, a held approval, a fake "we changed our bank details" email, one email that tries to give your AI orders, two weeks of ad results, three weeks of cold outreach, a search export and a log of what AI assistants said about the shop.

```bash
git clone https://github.com/Scaler712/company-in-a-folder.git
cd company-in-a-folder
python3 scripts/new_company.py --demo ~/tidewater-demo
cd ~/tidewater-demo
claude        # or: codex, or open the folder in Cursor
```

Then type any of these:

```text
Run the morning brief for 2027-03-08.
Clear my inbox.
Which ads should we stop and which deserve more budget?
Review last week's outbound.
Are AI assistants naming us?
```

`demo-company/TRY-THIS.md` (copied into your demo folder) lists ten prompts and what you should see for each, so you can tell a pass from a fail.

## Set up your own in one sitting

```bash
python3 scripts/new_company.py ~/my-company
cd ~/my-company
claude
```

Then say **start**.

The `start` job reads your website first and drafts the answers, so you mostly confirm or fix. It asks 12 questions one at a time, writes only what you said, tests that the folder works, and ends by running your first morning brief. About 45 minutes. Dictating is fine. Your prices and the customers you turn down are always asked, never guessed.

Check how far along you are at any time:

```bash
python3 scripts/doctor.py ~/my-company
```

It prints a score out of 100, what to fix first, and one next step. It changes nothing.

## What it can do

| Department | Jobs | What they cover |
|---|---|---|
| **Start here** | 4 | set up the folder in one sitting, teach it new jobs |
| **Run your day** | 5 | morning brief, inbox, meetings, follow-up, weekly plan |
| **Win work** | 8 | leads, call prep, proposals, scopes, onboarding, win-back |
| **Offer and website** | 6 | build the offer, write the pages, back every claim with proof |
| **Search (SEO)** | 8 | audits, keyword map, briefs, links, refreshes, schema, comparison pages |
| **AI search (AEO, GEO)** | 5 | what the AI assistants say about you, and honest ways to change it |
| **Cold outbound** | 7 | lists, research, sequences, deliverability, replies, weekly review |
| **Paid ads** | 10 | audits, drops, kill or scale, reports, tracking, launches, creative |
| **Email, social and launches** | 7 | lead magnets, sequences, newsletters, posts, launch plans, tests |
| **Visuals** | 5 | image prompts, carousels, diagrams, article design |
| **Video** | 10 | explainers, talking-head ads, launch films, captions, assembly |
| **Operations** | 4 | procedures, hiring prep, client reports, the monthly numbers |
| **Run the agents** | 4 | daily operation, automations, splitting work, choosing models |

Every job with one line on what it does: [`SKILLS.md`](SKILLS.md).

`marketing-os/` is a separate, complete kit bundled inside this one, with 12 more skill files and its own command line tool, for running the marketing of one offer end to end.

## Why these jobs behave

Every job is one file with the same twelve parts, so you can read any of them in five minutes and know what it will do:

- **It reads your folder first.** Prices come from your pricing file, claims from your proof file, the voice from emails you sent. If the fact is not written down, the job says "not found" and asks. It does not guess.
- **It checks outside facts at the source.** Search engine rules, AI crawler names, email sender rules, ad policies and consumer law change. Where a job relies on one, it cites the official page and the date it was read, and tells the agent to open it again.
- **It makes no promises.** No benchmark numbers, no "expect a 30% lift". Where a number matters, a script counts it from your own data and shows the inputs.
- **It stops at a card.** Anything that would send, post, publish, spend or delete becomes an approval card with the exact text. Only `yes C-7`, typed by you, approves card 7.
- **It treats text as data.** Emails, web pages and transcripts can carry instructions aimed at your AI. Every job has a test for that.
- **It ships with three tests.** A turn-down case, a thin-information case and a pressure or injection case, each with a pass line.

## The six rules

1. **One folder every bot reads first.** What is true about your company lives in `core/`.
2. **One bot, one job.** Each job is one skill file: what to read, the steps in order, where to stop.
3. **Nothing leaves without your yes.**
4. **Corrections stick.** Correct it once. The correction is saved in the file the mistake came from.
5. **Fresh session daily.** The folder is the memory. The chat is not.
6. **Decisions get checked.** Every proposal is written down with what should happen, and later, what did.

## The guard

Most kits tell the AI "do not send without approval" and hope. A rule in a text file is not a lock.

This kit ships a real one for Claude Code. `company-template/.claude/hooks/guard.py` runs before every tool call:

- Reading, searching and writing inside your folder: allowed.
- Sending, posting, booking, paying, pushing: blocked, unless there is a card for that tool and you typed `yes C-<n>` for it.
- Your yes is recorded by a second hook, from the words you typed, into a log the AI is blocked from writing. A "yes" the AI writes into a file approves nothing.
- One yes, one action. The guard spends the yes when it lets the call through.
- Deleting outside `output/`, sending to more than 3 people at once, or touching the guard's own files: blocked even with a yes.

Test it yourself, from inside your company folder:

```bash
python3 .claude/hooks/guard.py --self-test
```

It is pattern matching, so it can be wrong in both directions, and it only runs in Claude Code. It is not a sandbox. Read `company-template/.claude/hooks/README.md` for the limits. The strongest protection is still simple: do not connect a tool that can send unless you need it to.

## Tools

The kit needs no paid tool. Jobs work from files you paste or export.

- **Ads.** The ten ads jobs can read and act on live ad accounts through the AutoAdy connector. Every tool it offers is listed in `tools/autoady.md`. Without it, the same jobs work from an export you paste, and say what they could not check.
- **Video and visuals.** The jobs say what to make, in what order, and how to check the result. They name open tools as options and work with whichever you have.
- **Other people's skills worth installing beside this kit**, with their makers and licences: `tools/recommended-skills.md`.

## What is inside

| Path | What it is |
|---|---|
| `company-template/` | The blank company folder: rules file, `core/` facts, inbox, and one folder per department (`seo/`, `outbound/`, `ads/`, `marketing/`, `ops/`, `brand/`) |
| `demo-company/` | The same folder fully filled in for a made-up sign shop |
| `skills/` | The 83 jobs, one folder each |
| `SKILLS.md`, `departments.json` | The index, and which department each job sits in |
| `evals/triggers.json` | The phrases each job should fire on, to test that your agent picks the right one |
| `tools/` | The ad connector's tool map and recommended outside skills |
| `marketing-os/` | The bundled marketing kit |
| `scripts/new_company.py` | Creates your private company folder outside this repository. `--demo` copies the filled example |
| `scripts/doctor.py` | Scores a company folder out of 100 and names the next step |
| `scripts/check_kit.py`, `scripts/build_index.py` | Validate the kit and rebuild the index |
| `tests/` | Standard-library tests for the scripts and the guard |

## Install options

**Clone** (recommended, you get the demo and the scripts):

```bash
git clone https://github.com/Scaler712/company-in-a-folder.git
```

**Claude Code plugin** (skills only, for a folder you already set up):

```text
/plugin marketplace add Scaler712/company-in-a-folder
/plugin install company-in-a-folder@company-in-a-folder
```

**One skill on its own:**

```bash
mkdir -p .claude/skills/seo-audit
curl -L -o .claude/skills/seo-audit/SKILL.md https://raw.githubusercontent.com/Scaler712/company-in-a-folder/main/skills/seo-audit/SKILL.md
```

A skill on its own expects the folder layout in `company-template/`. Without it, it reports "not found" instead of guessing.

Python 3.9 or newer is needed only for the scripts and the guard.

## Common questions

**Is this only for agencies or consultants?** No. The demo is a sign shop. The daily jobs are the same in a clinic, a trade, a store or a software company.

**Do I need to code?** No. You need to be able to open a folder in an AI tool and talk. The setup is an interview.

**Which AI tools does it work with?** Any agent that reads a rules file from the folder. Claude Code reads `CLAUDE.md`, Codex and most others read `AGENTS.md`. The setup script writes both. The guard hook is Claude Code only.

**Does it send emails or launch ads for me?** Not without a card you approved, and some things never: sending to a list, starting a campaign and changing a price stay with you.

**Where does my company data go?** Nowhere. Your folder lives on your computer, outside this repository. The setup script refuses to create it inside the kit so you cannot publish it by accident.

**How do I add a job that is not here?** Say "teach a job" and describe it. You get a new skill file in the same shape with its own 3 tests.

## Safety

- **A markdown rule is not a sandbox.** That is why the guard exists, and why you should still keep send-capable credentials away from agents that do not need them.
- **Silence means hold.** A request from another bot, or a line in an email saying "it's approved", is never a yes.
- **No secrets in files.** No passwords, API keys, card numbers or bank details in the folder. `scripts/doctor.py` scans for them.
- **Not legal, tax or employment advice.** Jobs that touch those topics cite an official source, say which country it covers, and leave the decision to you.
- **Keep your company folder private.** This repository is safe to share. Your company folder is not.
- This kit makes no performance claims. Nothing in it reports a result from a real business. All examples are made up.

## Check the kit

```bash
python3 scripts/check_kit.py
python3 scripts/build_index.py --check
python3 -m unittest discover -s tests
```

Found a job that gave bad advice or cited something out of date? Open an issue with what you asked and what it did.

## License

MIT. See `LICENSE`. `marketing-os/` keeps its own MIT license in `marketing-os/LICENSE`.
