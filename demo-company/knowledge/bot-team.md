# Bot team

Which bot does which job. One row per bot. One job per bot.
The `bot-team` skill helps you fill this. Start with 2 rows, not 7.

| Bot | Job (skill) | Reads | May write inside the folder | Tools it may use | Runs when | Owner of its cards |
|---|---|---|---|---|---|---|
| Lead desk | process-a-lead | `core/`, `corrections.md`, `communication/emails-i-sent.md`, `contacts/` | `output/`, `contacts/`, `log/cards.md` | Read-only mail view, public web pages | On request, and once each morning on the overnight inbox | Owner |
| Quote desk | write-a-proposal | `core/`, `corrections.md`, `sales/`, the quote log on the shared drive | `output/`, `sales/won/`, `log/cards.md` | Read-only shared drive | On request, after a site measure | Owner |

Neither bot has a send button. The owner sends from the shared inbox by hand.

## Schedule

| Time | What runs | Model or script |
|---|---|---|
| Start of day | Fresh session for every bot | none |
| 07:30 weekdays | Lead desk reads the overnight inbox and shows cards | the agent, by hand for now |
| Monday 08:00 | weekly-plan prep pass, no owner needed | the agent |

## Never scheduled

Sending, posting, booking, paying, or any change outside this folder. Those wait for a card.
