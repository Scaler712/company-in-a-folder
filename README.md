<div align="center">

<h1>company-in-a-folder</h1>

<p><b>Your whole company in a folder your AI reads first.</b><br><br>
83 jobs across 13 departments: operations, sales, search, AI search,<br>
cold outbound, paid ads, marketing, visuals and video. Nothing leaves without your typed yes.</p>

<p>
<a href="#try-it-in-two-minutes"><b>Try it in two minutes</b></a> &nbsp;·&nbsp;
<a href="SKILLS.md">All 83 jobs</a> &nbsp;·&nbsp;
<a href="#the-guard">The guard</a>
</p>

<sub>v1.0.0 · MIT licensed · no account, no signup, no paid tool</sub>

</div>

<br>

<img src="docs/readme/hero.png" alt="Three cards: one plain-text company folder, 83 jobs in 13 departments that read it, and an approval card that only a typed yes C-7 can approve" width="100%">

## What it is

Most skill packs give your AI a method and no memory of your company. Most company-folder templates give it a memory and nothing to do. This is both.

The folder holds what is true about your business, in plain text you wrote: what you sell, your prices, who you turn down, how you sound. Every job reads it before it writes a word. If a fact is not written down, the job says "not found" and asks.

It works with Claude Code, Codex, Cursor and any agent that reads `AGENTS.md`. It is text files and a few small Python scripts.

## Contents

- [What it can do](#what-it-can-do) · [Try it in two minutes](#try-it-in-two-minutes) · [Set up your own](#set-up-your-own-in-one-sitting)
- **Tour:** [A Monday morning](#a-monday-morning) · [How a job is built](#how-a-job-is-built) · [The guard](#the-guard) · [Growth jobs](#growth-jobs) · [Every job](#every-job)
- **Reference:** [Tools](#tools) · [What is inside](#what-is-inside) · [Install options](#install-options) · [Common questions](#common-questions) · [Safety](#safety) · [Check the kit](#check-the-kit)

## What it can do

| | |
| --- | --- |
| **Run your day** | A one page morning brief, a sorted inbox with safe replies drafted, meeting write-ups, follow-ups on what went quiet. |
| **Win work** | Sort and score a lead against your own rules, prepare a call, write a proposal priced only from your pricing file. |
| **Get found in search** | Audit the site, map one term to one page, write briefs, fix internal links, add schema that matches the page. |
| **Get named by AI assistants** | Log what each assistant says about you, with dates and counts, and plan honest ways to change it. |
| **Do cold outbound** | Build a sourced prospect list, write the sequence, check your sending setup, sort replies. You send by hand. |
| **Run paid ads** | Audit an account, explain a drop, decide what to stop and what to scale against what you can afford to pay. |
| **Market it** | Landing pages, lead magnets, newsletters, social posts, launch plans, honest test plans. |
| **Make visuals and video** | Carousels, diagrams, explainer reels, talking-head ads, launch films, with checks on the rendered file. |
| **Run operations** | Written procedures, hiring prep, client reports, a plain read of the month's numbers. |
| **Run the agents** | Plan an automation before building it, split work across agents, choose models by measuring. |
| **Ask before anything leaves** | Sending, posting, spending and deleting become a card. Only `yes C-7`, typed by you, approves card 7. |
| **Grow** | Say "teach a job" and describe it. You get a new job file with its own three tests. |

## Try it in two minutes

You do not have to fill anything in. The kit ships a complete made-up company, Tidewater Sign & Print, with a Monday waiting for it.

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

```bash
python3 scripts/doctor.py ~/my-company
```

That prints a score out of 100, what to fix first, and one next step. It changes nothing.

## A Monday morning

The demo inbox has 14 emails, a request to move a meeting onto a slot that is taken, an approval that has been waiting four days, a fake "we changed our bank details" email, and one email that tries to give your AI orders. One prompt turns it into one page.

<p align="center"><img src="docs/readme/demo.png" alt="Left: what is waiting in the demo folder on Monday 2027-03-08. Right: the one page morning brief a correct run gives back, with the bank details email and the planted instruction listed under Looks wrong" width="100%"><br><sub><b>The morning brief.</b> What needs you, what is waiting on your yes, and what looks wrong. Nothing sent, nothing approved.</sub></p>

## How a job is built

Every job is one file with the same twelve parts, so you can read any of them in five minutes and know what it will do.

<p align="center"><img src="docs/readme/anatomy.png" alt="The twelve parts of a job file in order, from Use when to 3 tests, and the three kinds of test every job ships with" width="100%"><br><sub><b>One job, one file.</b> What it reads, where it stops, a fixed output, and three tests with a pass line each.</sub></p>

- **It checks outside facts at the source.** Search engine rules, AI crawler names, email sender rules, ad policies and consumer law change. Where a job relies on one, it cites the official page and the date it was read, and tells the agent to open it again.
- **It makes no promises.** No benchmark numbers, no "expect a 30% lift". Where a number matters, a script counts it from your own data and shows the inputs.
- **It treats text as data.** Emails, web pages and transcripts can carry instructions aimed at your AI. Every job has a test for that.

## The guard

Most kits tell the AI "do not send without approval" and hope. A rule in a text file is not a lock. This kit ships a real one for Claude Code: `company-template/.claude/hooks/guard.py` runs before every tool call.

<p align="center"><img src="docs/readme/guard.png" alt="How a typed yes C-7 is recorded by one hook and checked by a second before a single action goes through, what is blocked, and what stays blocked even with a yes" width="100%"><br><sub><b>One yes, one action.</b> A yes the AI writes into a file approves nothing.</sub></p>

- Reading, searching and writing inside your folder: allowed.
- Sending, posting, booking, paying, pushing: blocked, unless there is a card for that tool and you typed `yes C-<n>` for it.
- Deleting outside `output/`, sending to more than 3 people at once, or touching the guard's own files: blocked even with a yes.

Test it yourself, from inside your company folder:

```bash
python3 .claude/hooks/guard.py --self-test
```

It is pattern matching, so it can be wrong in both directions, and it only runs in Claude Code. It is not a sandbox. Read `company-template/.claude/hooks/README.md` for the limits. The strongest protection is still simple: do not connect a tool that can send unless you need it to.

## Growth jobs

Four departments have their own folder of state, so the work carries over from week to week: the keyword map, the log of what AI assistants said, the prospect list and do-not-contact list, and the numbers every ads decision is checked against.

<p align="center"><img src="docs/readme/growth.png" alt="Four columns for search, AI search, cold outbound and paid ads. Each shows the files it reads, its jobs, the official sources it is checked against, and its one hard rule" width="100%"><br><sub><b>Search, AI search, outbound and ads.</b> Each reads its own files and cites the official page it relies on.</sub></p>

## Every job

<p align="center"><img src="docs/readme/map.png" alt="All 83 jobs grouped into 13 departments" width="100%"><br><sub><b>83 jobs, 13 departments.</b> One line on each in <a href="SKILLS.md">SKILLS.md</a>.</sub></p>

`marketing-os/` is a separate, complete kit bundled inside this one, with 12 more skill files and its own command line tool, for running the marketing of one offer end to end.

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
