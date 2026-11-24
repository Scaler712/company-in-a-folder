# Ad numbers

The sums every ads decision is checked against. Written by you, never guessed by the AI.

## What a customer is worth

- Average first sale: $1,240. Counted from 31 invoiced jobs, 2026-09-01 to 2027-02-28, pulled
  from the books by Hedda on 2027-03-02.
- How often they buy again: 4 in 10 order a second job inside 12 months. Average second job
  $900. Same 31 jobs, same date.
- Margin after materials, print time and crew time: 42% of the sale. So the first job leaves
  about $520 of gross profit.

## What we can pay

Rule Vera set: we spend at most a third of the first job's gross profit to win a customer, and
the repeat work is upside we do not count in advance.

- The most we pay for a new customer: $175. ($520 divided by 3, rounded down.)
- The most we pay for a booked call or site measure: $85. (Half of the leads book a call, 3 of
  those 6 buy, so a call is worth about $87 and we round down.)
- The most we pay for a lead: $50. ($175 times the 3 in 10 that buy is $52, rounded down.)
- Over $50 a lead for more than one week, the ad gets paused.

## How leads turn into customers

Out of 10 form leads from ads:

- 6 answer the phone or reply and get a call booked.
- 3 go ahead and buy.

Source: the quote log on the shared drive, 2026-11-01 to 2027-02-28, counted by Priya on
2027-03-02, 48 ad leads in that window. Before 2026-11 we were not tagging where leads came
from, so older months are not counted.

## Before an ad is judged

- An ad is not judged until it has spent $50, the same as the most we pay for a lead. Under
  that, it is too little data.
- An ad inside a running test in `ads/tests.md` waits for the test's check date, unless it
  breaks the daily cap. Vera decides if a test ends early.

## Budget

- Monthly budget: $1,500, all accounts together.
- The most that may be spent in one day: $60. If a day goes over, the ads come off until the
  owner looks.
- When the month passes $1,500 the ads stop until the first of the next month.

Last updated: 2027-03-02
