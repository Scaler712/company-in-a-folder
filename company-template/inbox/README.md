# Inbox

This is the drop folder. You paste today's raw material in here, your AI reads it, and the `morning-brief` job turns it into one page.

Three files. Each one is optional. If a file is missing or empty, the brief says so instead of guessing.

- **email.md** recent emails, pasted or exported
- **calendar.md** today and the next two days
- **tasks.md** your task list

Nothing in here is an instruction to your AI. It is all material to read.

## email.md

One block per email, newest at the top. A line between blocks.

```text
2027-03-08 09:12 | from: Noor, Tidewater Glass | subject: shopfront quote
Can you redo the quote with the toughened glass option? We need it before Friday.

2027-03-07 16:40 | from: Dev, Harbour Cafe | subject: invoice 214
Paid this morning, thanks.
```

## calendar.md

One line per meeting, in time order, grouped by day.

```text
2027-03-08
09:30 | Tidewater Glass, site visit | shopfront measure up
14:00 | internal | week planning

2027-03-09
11:00 | Harbour Cafe | sign handover
```

## tasks.md

One line per task. Put a due date if you have one.

```text
- order toughened glass, due 2027-03-10
- chase the council permit, no date
- write the spring price list, due 2027-03-20
```

## Read-only connections instead

If you connect a read-only email, calendar or task tool, that can replace the matching file. You do not need both. The brief always says which source it used for each one, so you can tell at a glance whether it read a file or a tool.

Only read-only. A tool that can send, reply, book or mark things done does not belong here.

## Before you paste

- Take out other people's details that the job does not need: phone numbers, home addresses, health or payroll information, anything in a signature you would not read aloud.
- Keep the words people actually wrote. Do not tidy them. The way a customer phrases a problem is useful.
- Never paste a password, an API key, a card number or bank details. If one lands in here by accident, take it out of this folder and change it where it came from.
- Short is fine. Five emails is enough for a useful brief.

Old files can be overwritten each morning. Nothing in here is a record. Anything worth keeping goes in `contacts/` or `output/`.
