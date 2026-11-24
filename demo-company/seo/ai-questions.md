# Questions buyers ask AI assistants

The fixed list of questions we check, and a dated log of the answers. Same questions every time, so weeks can be compared.

The two assistants are written as "Assistant A" and "Assistant B" so the rows stay comparable
even if we change which chat tool we use. Both were asked with web search on, in a fresh chat,
with no company name and no extra context. A is the one the owner uses on her phone, B is the
one in the shop browser.

## The questions

1. who makes shop front signs near fairhaven
2. how much does a full van wrap cost for a trade fleet
3. best sign company for a small cafe front
4. who can wrap 5 vans for a plumbing firm
5. where can i get event banners printed for a club
6. how long does a shop sign take from measure to install

## Log

| Date | Question no. | Assistant | Were we named | Who else was named | Sources it showed |
|---|---|---|---|---|---|
| 2027-02-22 | 1 | Assistant A | no | Gullwing Graphics, Saltmarsh Sign Works, Pierhead Print & Display | https://baydirectory.example/signs, https://gullwing-graphics.example/ |
| 2027-02-22 | 1 | Assistant B | no | Saltmarsh Sign Works, Baywide Signs | https://baydirectory.example/signs |
| 2027-02-22 | 2 | Assistant A | no | none, it gave a price range only | https://wrapcostguide.example/van-wraps |
| 2027-02-22 | 2 | Assistant B | no | Pierhead Print & Display | https://pierhead-print.example/wraps, https://wrapcostguide.example/van-wraps |
| 2027-02-22 | 3 | Assistant A | no | Gullwing Graphics, Two Rivers Signage | https://fairhavenbulletin.example/best-of-the-bay |
| 2027-02-22 | 3 | Assistant B | no | Gullwing Graphics | https://fairhavenbulletin.example/best-of-the-bay |
| 2027-02-22 | 4 | Assistant A | no | Baywide Signs, Pierhead Print & Display | https://fleetnews.example/wrap-suppliers |
| 2027-02-22 | 4 | Assistant B | no | none, it said to search locally | no links shown |
| 2027-02-22 | 5 | Assistant A | yes, as "Tidewater Sign & Print" | Saltmarsh Sign Works | https://tidewater-signs.example/banners, https://baydirectory.example/print |
| 2027-02-22 | 5 | Assistant B | no | Saltmarsh Sign Works, Baywide Signs | https://baydirectory.example/print |
| 2027-02-22 | 6 | Assistant A | no | none, it answered in general steps | https://signmakersguide.example/lead-times |
| 2027-02-22 | 6 | Assistant B | no | none, it answered in general steps | no links shown |
| 2027-03-01 | 1 | Assistant A | yes, as "Tidewater Sign and Print" | Gullwing Graphics, Saltmarsh Sign Works | https://tidewater-signs.example/shop-front-signs, https://baydirectory.example/signs |
| 2027-03-01 | 1 | Assistant B | no | Saltmarsh Sign Works, Baywide Signs, Two Rivers Signage | https://baydirectory.example/signs |
| 2027-03-01 | 2 | Assistant A | no | Pierhead Print & Display | https://wrapcostguide.example/van-wraps |
| 2027-03-01 | 2 | Assistant B | no | Pierhead Print & Display, Baywide Signs | https://pierhead-print.example/wraps |
| 2027-03-01 | 3 | Assistant A | yes, as "Tidewater Sign & Print" | Gullwing Graphics | https://tidewater-signs.example/our-work, https://fairhavenbulletin.example/best-of-the-bay |
| 2027-03-01 | 3 | Assistant B | no | Gullwing Graphics, Two Rivers Signage | https://fairhavenbulletin.example/best-of-the-bay |
| 2027-03-01 | 4 | Assistant A | no | Baywide Signs | https://fleetnews.example/wrap-suppliers |
| 2027-03-01 | 4 | Assistant B | no | Baywide Signs, Pierhead Print & Display | https://fleetnews.example/wrap-suppliers |
| 2027-03-01 | 5 | Assistant A | yes, as "Tidewater Sign & Print" | Saltmarsh Sign Works | https://tidewater-signs.example/banners |
| 2027-03-01 | 5 | Assistant B | yes, as "Tidewater Signs" | Saltmarsh Sign Works, Baywide Signs | https://tidewater-signs.example/banners, https://baydirectory.example/print |
| 2027-03-01 | 6 | Assistant A | no | none, it answered in general steps | https://signmakersguide.example/lead-times |
| 2027-03-01 | 6 | Assistant B | no | none, it answered in general steps | no links shown |

## What changed between the two runs

- Run 1, 2027-02-22: named in 1 of 12 rows. Run 2, 2027-03-01: named in 4 of 12 rows.
- New in run 2: question 1 on Assistant A and question 3 on Assistant A, both citing our own
  pages. Question 5 on Assistant B named us for the first time.
- Lost nothing between the runs.
- Two runs is two data points, not a trend. Nothing here says why anything moved.
- Referral traffic from assistants: not checked. No analytics pasted and no connector attached.

## Wrong facts the answers gave about us

- 2027-03-01, Assistant B, question 5: called us "Tidewater Signs" and said we offer "same day
  banner printing". We do not take any work inside 48 hours (`core/clients.md`).
- 2027-03-01, Assistant A, question 3: said we are "in the harbour district". The shop is on the
  print road side of town. Small, but worth fixing on the contact page.

## Who else keeps coming up

Gullwing Graphics, Saltmarsh Sign Works, Baywide Signs, Pierhead Print & Display and Two Rivers
Signage. All five are made up for this demo folder. In a real folder these would be the names
your buyers are being handed instead of yours.
