# Blind scores — model transfer v1

These scores use `REVIEWER_RUBRIC.md` only. The generators did not receive this file or any coaching about what to notice.

Each run was a fresh model context. It was allowed to read one packet file and then received only the wrapper for that test. Creative OS provider execution stayed disabled. These were not logged-in grok.com or chatgpt.com web chats.

| Run | Model | Packet |
| --- | --- | --- |
| A | Grok 4.7 | `target_story_development_packet.md` |
| B | GPT-5.6 Terra | `target_story_development_packet.md` |
| C | Grok 4.7 | `maria_concept_generation_packet.md` |
| D | GPT-5.6 Terra | `maria_concept_generation_packet.md` |

Scale: 0 missing or contradicted, 1 present but thin, 2 specific and consistent with the packet.

## Target story audit

| Item | A Grok | B GPT |
| --- | --- | --- |
| Preserves good decisions | 2 | 2 |
| Story before commerce | 2 | 2 |
| Human causality | 2 | 2 |
| Specific stakes | 2 | 2 |
| Comment doors | 2 | 2 |
| Viral texture | 2 | 2 |
| Secondary inspection | 2 | 2 |
| Commerce integration | 2 | 2 |
| Proof boundary | 2 | 2 |
| Continuity | 2 | 2 |
| Retailer language | 2 | 2 |
| Basket padding | 2 | 2 |
| Production-ready judgment | 2 | 2 |
| Total | 26/26 | 26/26 |

Both returned `StoryDevelopmentAuditResult` JSON, status `READY`, and a preserve list. Neither rewrote the story.

Grok named one small repair: clear external id `85978615` from the AirPods 5 row, because the prose lock marks that TCIN as the superseded AirPods 4 id. It left generation, title, price, and placement alone. It also restated the rejected extras (lone gold "1", AirPods Pro 3, relighting candles, $99.99 sale) as things to keep rejected.

GPT found no story-level change. Its diagnosis is the same arc: the don't-look line, the birthday stake, the nosy dare, AirPods as a hidden gift, paper towels as the cover, secondary discount, and proof that stops at the order surface. It did not mention the stale TCIN. That is a deeper read by Grok, and the narrative judgment is still READY for both.

## Maria concept generation

| Item | C Grok | D GPT |
| --- | --- | --- |
| Account fit | 2 | 1 |
| Age world | 2 | 2 |
| Novelty | 1 | 2 |
| Story-native commerce | 2 | 2 |
| Comment doors | 2 | 2 |
| Viral texture | 2 | 2 |
| Research flags | 2 | 2 |
| Economics | 2 | 2 |
| Proof surface | 2 | 2 |
| Total | 17/18 | 17/18 |

Both returned five `ConceptDraft` objects. Neither copied Chick-fil-A, the pink iPad winner, the MacBook post, or the Target birthday story. Neither invented a price or padded a basket. Unknown prices are marked research needed.

Grok uses Maria's lane directly, including Dre in "the plain bag was on purpose", and keeps electronics off the account. Three of the five premises share one skeleton: a public claim is settled by the order surface (edited order, stolen credit, mom thinks she cooked). The other two, the plain bag and the dorm host, are different events. The system transferred, and the claim-versus-proof pattern is over-represented.

GPT spreads the five events further apart: volunteered snack table, dorm-elevator goodbye, protective sleepover, spicy-food alibi, post-exam comfort night. It uses food, couples, family, and first-year settings. It never uses the name Dre from the approved DNA, so account fit is thinner.

Both treat commerce as secondary or absent when a discount would only cheapen an order the person already wanted. That is the operating system, not a missing ad.

## What this says

The Target audit transferred to both models. A fresh model can evaluate this story from the packet: preserve the working decisions, keep commerce secondary, and avoid a rewrite.

The Maria batch transferred the creative rules to both models: age world, comment doors, inspectable details, research flags, and no discount padding. The remaining gap is variety of premise shape, plus GPT not binding the approved relationship name. That gap belongs in how concept-generation context teaches "five different skeletons," not in a one-off prompt added at chat time.
