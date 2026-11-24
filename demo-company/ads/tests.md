# Ad tests

One block per test. One thing changed at a time.

```text
T-<n> | <date started> | account: <name> | where: <campaign or ad set>
changed: <the one thing that is different>
kept the same: <everything else>
we expect: <result, with the number and the date we will look>
what happened: <filled in on the check date, from the account, with the dates read>
decision: <keep, stop, or test again, and why>
```

```text
T-1 | 2027-02-08 | account: Tidewater Sign & Print | where: Fleet van wraps, ad set Trade fleets 5 to 30 vans
changed: the opening line of the ad, from "Professional vehicle graphics" to the words a buyer
  used on the phone, "we bought three vans and they are still white"
kept the same: image, audience, placements, budget, the form and its 4 fields
we expect: cost per lead under the $50 ceiling in ads/numbers.md over a full week, checked 2027-02-22
what happened: read 2027-02-22 for 2027-02-15 to 2027-02-21. Buyer words ad: $12.90 a lead on
  6 leads. Old opening line: $31.40 a lead on 2 leads. Both under the ceiling, the buyer words
  one by a lot, on small numbers.
decision: keep the buyer words line, and use the same approach on the shop front sign ads. 6
  leads against 2 is not proof, so the old line stays switched off rather than deleted.
```

```text
T-2 | 2027-02-25 | account: Tidewater Sign & Print | where: Fleet van wraps, ad set Lookalike van owners
changed: the audience only, a lookalike built from past wrap customers instead of the trade
  fleet interest list
kept the same: both ads, the budget, the placements, the form
we expect: cost per lead at or under $50, the same ceiling, with at least 4 leads to look at.
  Check on 2027-03-10.
what happened:
decision:
```

```text
T-3 | 2027-03-06 | account: Tidewater Sign & Print | where: Shop front signs, ad set Local business owners
changed: the image, from a finished sign on a wall to a photo of the crew installing it
kept the same: headline, body, audience, budget, placements
we expect: more clicks per thousand views than the finished sign image, over a full week.
  Check on 2027-03-15.
what happened: started 2027-03-06, two days of data only as of 2027-03-08. Too early to read.
decision:
```
