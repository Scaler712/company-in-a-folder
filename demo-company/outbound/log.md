# Outbound log

One line per message you sent, added after you send it. The AI never sends.

In the Reply cell, start with the date the reply arrived, then a colon, then their words:
`2027-03-02: "Do you take an old wrap off?"`. Leave the cell empty if nothing came back.
The weekly review counts a reply in the week it arrived, not the week the message went out,
so the date in that cell is the only thing that puts it in a week.

Every row below was typed and sent by Vera herself through the other company's own contact form,
in the evening, usually five or six at a time. Nothing here was sent by a bot.

| Date | Company | Person | Channel | Message no. | Reply | Next step |
|---|---|---|---|---|---|---|
| 2027-02-19 | Alder and Pike Builders | Yusuf | contact form | 1 |  | wait 5 working days |
| 2027-02-19 | Harrow Lane Joinery | Mo | contact form | 1 |  | wait 5 working days |
| 2027-02-19 | Kelp Cove Plumbing | Ada | contact form | 1 | 2027-02-24: "We have four plain ones and I am tired of looking at them. What would the doors and rear cost on four, and how long do you need each van for?" | owner to answer the price question from the pricing file, then offer a measure |
| 2027-02-20 | Fenwick Drains | Gus | contact form | 1 | 2027-02-25: "Not now. Our vans go in for servicing through March. Ask me again in May and I will probably say yes." | noted May in the CSV, no further message until then |
| 2027-02-20 | Oyster Point Joinery | Caleb | contact form | 1 | 2027-02-27: "We use a shop up in the next county, they do all our stuff. Nothing wrong with you, we just have a guy." | marked not interested, no further message |
| 2027-02-20 | Tern Valley Plumbing | Esme | contact form | 1 |  | wait 5 working days |
| 2027-02-23 | Redfern Glazing | Pia | contact form | 1 |  | wait 5 working days |
| 2027-02-24 | Stonebridge Heating | Rolf | contact form | 1 |  | wait 5 working days |
| 2027-02-25 | Haddon Gas Services | Trevor | contact form | 1 |  | wait 5 working days |
| 2027-02-25 | Thistledown Landscapes | Bruno | contact form | 1 | 2027-03-02: "Two of ours have an old wrap on them that is peeling. Do you take that off, and is it extra?" | owner to answer with the written removal price, then offer a measure |
| 2027-02-26 | Harrow Lane Joinery | Mo | contact form | 2 | 2027-02-26: "Please stop writing to us." | added to do-not-contact the same day, row removed from the prospect list |
| 2027-02-26 | Wren Street Electrical | Idris | contact form | 1 |  | wait 5 working days |
| 2027-02-27 | Cobbleway Paving | Marta | contact form | 1 |  | wait 5 working days |
| 2027-03-02 | Alder and Pike Builders | Yusuf | contact form | 2 |  | last message, close the row if nothing comes back |
| 2027-03-02 | Pellow Bros Builders | Dermot | contact form | 1 |  | wait 5 working days |
| 2027-03-03 | Longmarsh Groundworks | Hania | contact form | 1 |  | wait 5 working days |
| 2027-03-03 | Redfern Glazing | Pia | contact form | 2 |  | last message, close the row if nothing comes back |
| 2027-03-03 | Stonebridge Heating | Rolf | contact form | 2 |  | last message, close the row if nothing comes back |
| 2027-03-04 | Haddon Gas Services | Trevor | contact form | 2 |  | last message, close the row if nothing comes back |
| 2027-03-04 | Tern Valley Plumbing | Esme | contact form | 2 |  | last message, close the row if nothing comes back |
| 2027-03-05 | Marlin Electrical | Faye | contact form | 1 |  | wait 5 working days |
| 2027-03-05 | Wren Street Electrical | Idris | contact form | 2 |  | last message, close the row if nothing comes back |
| 2027-03-06 | Driftwood Carpentry | Suki | contact form | 1 |  | wait 5 working days |

## Notes on this log

- Three weeks of sending, 2027-02-19 to 2027-03-06. 23 messages out, 16 first messages
  and 7 second messages, 5 replies. Each reply cell starts with the date that reply arrived.
- These counts are too small to tell one message apart from another. Do not call a winner yet.
- The stop request from Harrow Lane Joinery on 2027-02-26 went into `do-not-contact.md` the same
  day and the row came out of `prospects.csv`, which is why that company is in this log and not
  in the list.
- Two replies are waiting on the owner to answer a price question. Neither has a drafted reply:
  price answers are quoted from `core/pricing-and-limits.md` and the owner sends them.
