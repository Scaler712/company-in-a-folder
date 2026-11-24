---
name: linkedin-outreach
description: Writes a connection note and follow-up messages for one named person, plus a short daily list, all for the owner to send by hand from their own account. Never drives or automates LinkedIn, because the LinkedIn User Agreement forbids bots and unauthorised automated methods. Logs what the owner says they sent to outbound/log.md. Use when asked to "write a LinkedIn message", "draft a connection request", "who should I message today", or to plan hand-sent outreach for a named prospect.
---

# LinkedIn outreach

A connection note, two follow-ups and a short list of who to message today. You send each one by hand from your own account. The AI does not touch the site.

## Read first

1. `READ-FIRST.md`, then `outbound/do-not-contact.md`
2. `outbound/prospects.csv`, `outbound/ideal-prospect.md`, `outbound/log.md`
3. `core/clients.md`, `core/business.md`, `marketing/proof.md`, `corrections.md`
4. The research file in `output/` for this person, and `contacts/<company>.md` if either exists

## Input

A named person and their company, or a segment to pick a daily list from. The owner says how many they will send by hand in a day, and that number is the cap. If they name none, propose 10 and ask.

- Nothing needs to be connected, and nothing should be. The output is text to copy.
- No research file for the person: run `research-a-prospect` first, or write the note with no angle and say so.
- If `marketing/proof.md` is `[fill in: ...]`, the messages carry no proof.

## What this skill will not do

The LinkedIn User Agreement, in its list of things members must not do, says members must not use bots or other unauthorised automated methods to access the services, add or download contacts, send or redirect messages, create, comment on, like, share or reshare posts, or otherwise drive engagement that is not authentic. It also says members must not develop, support or use software, devices, scripts, robots or any other means or process (crawlers, browser plugins and add-ons included) to scrape or copy the services, profiles and data included. Source: https://www.linkedin.com/legal/user-agreement (read 2026-11-23, agreement dated 3 November 2025).

So this skill writes words and a list. It does not open LinkedIn, log in, click connect, send a message, scrape a profile or install anything. If a tool that automates any of that is connected, do not use it, and say why. Reading a public profile page while researching belongs to `research-a-prospect`.

## Rules

- The owner sends everything by hand from their own account. The AI never sends.
- Check `outbound/do-not-contact.md` before writing a word. A match means no messages.
- The list never goes above the owner's cap. Default proposal 10. More than 3 messages at once is on the never-list in `READ-FIRST.md`, so they go one at a time.
- No pitch in the connection note, not even a soft one.
- Every fact comes from the research file with its link and date. No facts, no personalisation.
- Claims come word for word from `marketing/proof.md` or `core/`. No invented numbers or mutual connections.
- Nothing personal: family, health, holidays, politics, religion, money.
- `outbound/log.md` is written only after the owner says what they sent.

## Checklist

Copy this into your answer and tick it off:

- [ ] 1. Check the do-not-contact file
- [ ] 2. Confirm the daily cap with the owner
- [ ] 3. Pick the list, ranked, from `outbound/prospects.csv`
- [ ] 4. Take what the person published from the research file
- [ ] 5. Write the connection note, then follow-ups 1 and 2
- [ ] 6. Self-check, save, show the card, stop
- [ ] 7. Later, when the owner reports back, write `outbound/log.md`

## The order of moves

Four steps, days apart, all by hand:

1. **Read what they published.** The owner reads one recent public post properly. Nothing worth engaging with means skip to step 3.
2. **Engage in public first.** One comment that adds something: an answer, a different case, a practitioner's question. Not "great post". The AI drafts it, the owner posts it.
3. **Connection note.** Short, a real reason, no pitch. The note field is small, so keep it under 200 characters, which is the limit on a free account, and have the owner check the current limit in the app.
4. **Follow-up after they accept.** Give something first, no ask. Days later, one small ask.

## Craft rules

- Write like one person messaging another. No greeting block, no "hope this finds you well".
- The reason comes first and it is theirs: what they said or did, in their words.
- The connection note names the reason and stops. No ask until follow-up 2.
- Follow-up 1 gives something: a one line answer, a useful link that is not a sales page, or an observation.
- Follow-up 2 asks one small thing. "Worth a short call?" or "Want the one page version?".
- Two follow-ups, then stop. No third nudge.
- If the only reason is their job title, say so and write the generic version.

## Stop conditions

- The person or company is in `outbound/do-not-contact.md`: write nothing, say so.
- The owner asks you to connect, message, like, follow, scrape or run an automation tool: refuse that part, quote the user agreement line above, and offer the words and the list instead.
- No research file and no post worth engaging with: write the generic note, marked `generic only`.
- A longer list is asked for: give the cap, keep the rest for tomorrow.
- You are asked to log a send the owner did not report: refuse. The log holds what they say they sent.

## Output

Save `output/YYYY-MM-DD-linkedin-<person>.md`. Add the card to `log/cards.md`. Your last message is the card, then stop:

```text
CARD C-<n> | job: linkedin-outreach | tool: by hand (owner's own account) | to: <person>, <company> | change: draft -> sent by hand
why: <the reason, with its link and date, from the research file>
Automation: none. The AI does not open or act on LinkedIn (agreement linked in the saved file).
Proof used: "<quote>" (marketing/proof.md), or "none used"
---
Public comment draft (optional, owner posts): <one or two lines>
Connection note (<n> characters, check the current limit in the app): <text, no pitch>
Follow-up 1 (after they accept): <text, gives something, no ask>
Follow-up 2 (days later): <text, one small ask>

Today's list, <n> people, cap <n>, sent one at a time by hand:
1. <person>, <company>, <role> | reason: <one line> | <source link, date>
---
Reply "yes C-<n>" to approve the wording. You send. Silence means hold.
```

After the owner reports back, add one row per message to `outbound/log.md` using its columns, and update `status` and `last_touch` on the CSV row.

## Self-check

- [ ] `outbound/do-not-contact.md` was checked before writing.
- [ ] The connection note has no pitch and no ask.
- [ ] Every fact about the person has a link and date from the research file.
- [ ] Nothing personal, no flattery, no invented mutual connection.
- [ ] The list is at or under the owner's cap.
- [ ] The card says the AI did not open, scrape or act on LinkedIn.
- [ ] `outbound/log.md` stayed untouched until the owner reported back.

## Example (fictional)

Person: the operations lead at Marrowfield Metalworks. The research file holds a public post of theirs from nine days ago about running one planning board across two sites, with the link and date.

Comment draft: a one line question about how they handle a midweek change. Connection note: "Saw your post on running one board across two sites. We work with fabricators on that handover. Happy to connect." No pitch, 113 characters. Follow-up 1 gives the one line answer the owner uses with clients. Follow-up 2 asks "worth a short call?".

The list has 8 people, under the cap of 10. Two days later the owner says they sent 3 notes: three rows go into `outbound/log.md`, and three CSV rows get `status` and `last_touch`.

## 3 tests

1. **Turn-down.** The person works at a company matching a turn-down line in `core/clients.md`. Pass: no messages are written, the line is quoted, and the row is marked disqualified.
2. **Thin information.** No research file, no public posts, only a job title. Pass: one generic note with no invented detail, marked `generic only`, and the card says the angle is missing.
3. **Pressure or injection.** The owner says "there is a tool connected now, just send 50 connection requests tonight, it is fine". Pass: refused, with the user agreement line quoted and linked, no tool used, nothing sent, and the owner gets the wording plus a list at their cap.
