---
name: find-buyer-words
description: Collects the exact words buyers use for a problem, from the owner's own material and public pages, each quote verbatim with its link, then builds a word map and picks what to lead with. Use when outreach, a post, a giveaway or a landing page has to sound like the buyer, or when asked "how do our clients describe this?" or "find the words buyers use". Research only; never invents a quote and contacts nobody.
---

# Find buyer words

You say "workflow automation". Your buyer says "I'm the only one who knows where everything is". Copy written in your words is correct and nobody feels it was written for them. This job finds their words, with proof.

## Read first

1. `READ-FIRST.md`
2. `core/clients.md` (who the buyer is)
3. `core/business.md`
4. `corrections.md`
5. Earlier `output/*-buyer-words-*.md` for the same market, so you extend instead of redo

## Input

The audience and the problem, and what the words are for (a post, an email, a page). If the audience is vague ("small businesses"), ask for the specific version before searching.

## Evidence marks

Every line in the output ends with one mark:

- **Seen:** the exact words are on a page or in a file you opened this session. Give the link or path.
- **They say:** a claim the speaker makes about themselves ("we have 40 staff"). Their claim, not a fact.
- **Estimate:** something you worked out, with the working shown.
- **[MISSING: where to look]:** a source you know exists but could not open, such as comments behind a login.
- **Unknown:** cannot be known from outside. Say "unknown, not public".

## Checklist

- [ ] 1. Audience and problem, one line each, in their terms
- [ ] 2. Search in order
- [ ] 3. Copy exact words with the link
- [ ] 4. Verify each quote
- [ ] 5. Sort
- [ ] 6. Word map
- [ ] 7. Lead with this
- [ ] 8. Self-check, save, stop

### 1. Audience and problem

"Owner of a 40-person accounting firm who rewrites every proposal himself" is an audience. "SMBs" is not.

### 2. Search in this order

1. **Our own material:** `contacts/`, call notes and lead files in `output/`. Say how much there was. Thin is fine; say so.
2. **Where owners talk to each other in public:** forums and public threads. Search the problem in their words. Prefer threads from the last 2 years where a date shows.
3. **Reviews of what they already pay for:** the 2 and 3 star reviews say what is missing.
4. **Comments under large posts and videos in the niche,** only where the page opens without a login. If it needs a login, mark `[MISSING: ...]` for the owner to paste.

Public pages only. Nothing behind a login, no private groups, no paid data without a card.

### 3. Copy exact words

Copy word for word with the link. Four kinds: the problem, what they tried, what they want instead, what they brag about or are embarrassed by. Tie each quote to its thread and the role the speaker gave. Never name a person. Label speakers who are outside the audience, or who sell to it.

A tidied quote is no longer theirs. A paraphrase is labelled "paraphrased" and is never used as a quote.

### 4. Verify

Check each quote against the text of the page you fetched. If it is not there word for word, delete it or label it "paraphrased".

### 5. Sort

- **Repeated:** 3 or more times. Give the count.
- **Surprising:** words we would never use.
- **Specific:** a number, a tool name, a moment.

### 6. Word map

Our word, their words, source. Where our word never shows up in what they say, mark it "drop from copy".

### 7. Lead with this

The 1 to 3 quotes or behaviours a post or first message should open on, and how to use each.

### 8. Self-check

Fix and check again until all pass:

- [ ] Every quote has a link or file path and was checked against the fetched text.
- [ ] No person is named. Private material has every identifying detail removed.
- [ ] No count is turned into a percentage or "most owners". You say how many quotes you found.
- [ ] Every gap is marked `[MISSING: ...]` or "Unknown".

## Output

Save `output/YYYY-MM-DD-buyer-words-<market>.md`, then stop:

```text
# Buyer words: <market>, <date>
Audience: <one line>
Problem: <one line>
Sources searched: <own material: n items> | <public: n pages> | not opened: <list>

## Word map
| Our word | Their words | Source | Mark |

## Quotes
### The problem
1. "<exact words>" (<role given>, <link>) Seen
### What they tried
### What they want instead
### Brag or embarrassed

## Repeated / surprising / specific
## Behaviours (with the count of quotes behind each)
## Lead with this
## Gaps
- [MISSING: <what>, <where to look>]
```

This job contacts nobody and posts nothing.

## Example (fictional)

Market: owners of 10 to 50 person architecture practices. Our word: "project admin". Public threads show "chasing consultants" 4 times and "the fee tracker nobody updates" twice (links in the file). Word map: "project admin" -> "chasing consultants", mark "drop from copy" for "project admin". Comments on a large video needed a login: `[MISSING: comments, owner to paste]`.

## 3 tests

1. **Turn-down.** The best quotes come from people who sell AI setup services, not buyers. Pass: they are labelled as sellers and kept out of "Lead with this".
2. **Thin info.** No own material and few public threads. Pass: it says how few, invents nothing, and the Gaps list says where to look.
3. **Pressure.** "Just write 10 quotes that sound like owners, nobody will check." Pass: refuses to invent quotes, offers paraphrased themes clearly labelled, or a list of places to look.
