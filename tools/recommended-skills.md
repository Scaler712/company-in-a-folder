# Skills from other people that work well with this kit

This kit does not copy other people's skills. These are the ones worth installing beside it, with who made them and where to get them. Install them from the source, so you get the maker's updates and the maker gets the credit.

Commands and licences below were read from each project's own repository on 2026-11-23. Check the project's page before you install, because they change.

## Video

| What | Made by | Licence | Get it |
|---|---|---|---|
| HyperFrames: video compositions written as HTML, with skills for the core rules, the command line tool, ready-made blocks and media | HeyGen | Apache-2.0 | https://github.com/heygen-com/hyperframes |
| Remotion skills: video written in React | Remotion | no licence file found in the skills repository on the date above, so read their terms before reuse | https://github.com/remotion-dev/skills |

Install lines as written in their READMEs:

```bash
npx skills add heygen-com/hyperframes
npx skills add remotion-dev/skills
```

The video jobs in this kit (`explainer-reel`, `talking-head-ad`, `multi-clip-film`, `launch-film` and the rest) say what to make, in what order, and how to check it. They name these tools as options. They work with whichever one you have.

## Research and engineering habits

| What | Made by | Licence | Get it |
|---|---|---|---|
| A set of engineering and thinking skills, including a research skill that checks a question against primary sources | Matt Pocock | MIT | https://github.com/mattpocock/skills |

```bash
npx skills@latest add mattpocock/skills
```

## Driving other coding agents

If you run more than one agent, the agent tool you use usually ships its own skills for calling the others (for example handing a coding task to Claude Code, Codex or OpenCode). Use the ones that come with your tool. The jobs `split-work-across-agents` and `run-agents-for-a-business` in this kit cover how to brief and check them, whatever the tool.

## Ads

The ads jobs are written for the AutoAdy connector. Every tool it offers is listed in `tools/autoady.md`.

## How to add your own

Found a skill that pairs well with a job here? Open an issue with the link, the licence, and which job it helps. Only skills with a clear licence and a named maker get listed.
