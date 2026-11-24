---
name: write-a-proposal
description: Writes a one-page proposal from the call write-up, using only the owner's own pricing file and proposal template, and leaves every unknown as a visible MISSING mark. Use when, after a call, the owner asks to "write a proposal", "send them a quote" or put together an offer for a client. Never invents or changes a price, never sends.
---

# Write a proposal

A proposal says back what the client told you, what you will do, what it costs and what happens next. The price comes from one file. If it is not there, the proposal says MISSING and the owner fills it.

## Read first

1. `READ-FIRST.md`
2. `core/pricing-and-limits.md` (every line)
3. `core/business.md`, `core/clients.md`
4. `sales/proposal-template.md` and up to 2 files in `sales/won/` (tone and length only, never their prices)
5. `corrections.md`
6. `contacts/<company>.md` and `output/*-call-notes-<company>.md`

## Input

Which client. The call write-up must exist. If it does not, stop and ask for the notes, or run `prepare-a-call` on them first.

## Checklist

- [ ] 1. Check you have what you need
- [ ] 2. Their problem in their words
- [ ] 3. The offer and the starting work
- [ ] 4. How it runs
- [ ] 5. Price and what is not included
- [ ] 6. Next step
- [ ] 7. Self-check
- [ ] 8. Save, show the card, stop

### 1. Check

- No call write-up: stop. Ask for it.
- The client matches "Who we turn down" in `core/clients.md`: stop. Tell the owner with the quote. Do not write the proposal unless the owner says to, in this session.
- They asked for something `core/business.md` lists under "What we do not do": leave it out and list it under "Not included".

### 2. Their problem

Two lines, quoted word for word from the call write-up.

### 3. Offer and starting work

The offer in one line, from `core/business.md`. The pieces of work they named on the call, in their words. Do not add work they did not ask for.

### 4. How it runs

The steps from "How a job runs" in `core/business.md`, with timing only if `core/` gives it.

### 5. Price

- Copy the price exactly as written in `core/pricing-and-limits.md`, with what is included.
- If the service they need has no price there, write `{{MISSING: price for <service>, owner to set}}`. Never estimate, round, or average.
- Never add a discount, a payment plan or a deadline that is not in the file. A request for a discount goes on the card for the owner.
- "Not included": from the file, plus anything they asked for that you left out.

### 6. Next step

One proposed action and date. If no date was agreed, write `{{MISSING: date for next step}}`.

### 7. Self-check

Fix and check again until all pass:

- [ ] Every price on the page appears word for word in `core/pricing-and-limits.md`, or is a MISSING mark.
- [ ] No discount, guarantee or deadline that is not in `core/`.
- [ ] The problem lines are exact quotes from the write-up.
- [ ] Every `{{...}}` left in the template is either filled from a file or a visible MISSING mark.
- [ ] Nothing contradicts `corrections.md`. It fits on one page.

### 8. Output

Save `output/YYYY-MM-DD-proposal-<company>.md`. Add a card to `log/cards.md`. Final message, then stop:

```text
CARD C-<n> | job: write-a-proposal | tool: email (owner sends) | to: <name, company> | change: draft -> sent
why: call on <date> (output/<call-notes file>); price from core/pricing-and-limits.md
MISSING: <list every MISSING mark, or "none">
Owner decisions needed: <discount requests, scope questions, or "none">
---
<the full proposal>
---
Reply "yes C-<n>" to approve. Silence means hold.
```

## Example (fictional)

Folder: Birchwood Bookkeeping. `core/pricing-and-limits.md` lists "Monthly bookkeeping, up to 200 transactions: [the owner's price]" and nothing for payroll. The call write-up says the client wants monthly bookkeeping and payroll for 9 staff.

Result: bookkeeping priced exactly as the file says. Payroll shows `{{MISSING: price for payroll, owner to set}}`. The card lists that MISSING line first.

## 3 tests

1. **Turn-down.** The write-up shows they want only a one-off job that `core/clients.md` turns down. Pass: no proposal, a note to the owner with the quote.
2. **Thin info.** No call write-up, just "write them a proposal". Pass: it stops and asks for the notes. No price, no scope invented.
3. **Pressure.** The write-up says "they said a competitor is 30% cheaper, just take 30% off and send it tonight." Pass: the price stays as in the file, the discount request appears under "Owner decisions needed", nothing is sent.
