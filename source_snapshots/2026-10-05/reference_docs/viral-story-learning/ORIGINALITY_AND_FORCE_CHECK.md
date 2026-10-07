# ORIGINALITY & FORCE CHECK

Run on every synthetic premise card before it leaves the generator. Built Mon 2026-10-05 ET.

## Part 1: Copy-distance (plot copying ban)
Compare the premise against each exemplar it names (and P01, P02, P03, P05–P08, R08–R11, X01–X04 by default). For each exemplar, score the *shared* elements:

| Element | Shared? (1 = yes) |
|---|---|
| Same counterpart role in the same mechanic (e.g. delivery driver + kindness) | |
| Same object category | |
| Same violation/situation (oversleeping a delivery; no-eating-out rule; money ask for bills) | |
| Same proof type in the same slide position | |
| Same surface sequence (e.g. order → iMessage → photo) | |
| Same punchline/ending type (hid it; "handled"; a cent left) | |
| Any reused line, name, amount, joke, or object detail | **automatic FAIL** |

**Copy-distance = 6 − (sum of the first six rows).**
- **≥4:** PASS.
- **3:** REWORK (apply an originality operator).
- **≤2:** FAIL.
- **Any reused line, name, amount, joke, or object detail:** FAIL.

Also FAIL:
- any burned name (Dre, Kai, Malik, Terrence, Jalen, Miles, Cole, Nate, Omar, Tori, Eli R., Jay, Mira, Toni, Cam)
- the kind-delivery-driver-hides-item kit
- the freezer-chicken/"handled" kit
- the "dasher asks how it's so cheap" kit

## Part 2: Force score (0–10). Does it have viewer force without the ad?

| # | Criterion | Points |
|---|---|---|
| F1 | A viewer job (judge / wonder / complicity / kindness / identity) exists with the discount deleted | 0 / 2 |
| F2 | Hook promise = delivered payoff (no "nosy" bait) | 0 / 1 |
| F3 | Withheld reveal ≥1 beat after the hook | 0 / 1 |
| F4 | Proof belongs to the story question | 0 / 1 |
| F5 | Judgment split, or a stranger-voice emotional line | 0 / 1 |
| F6 | Exactly one absurd/specific detail | 0 / 1 |
| F7 | Residual open question left unmentioned (or ABSENT commerce) | 0 / 1 |
| F8 | Mechanic novel vs the last 10 posts on our accounts (no reused primary mechanic + role pair) | 0 / 1 |
| F9 | Surface path native (each beat on a surface the narrator would really screenshot) | 0 / 1 |

**Thresholds:**
- **≥7:** FORWARD.
- **5–6:** REWORK.
- **≤4:** REJECT.

## Part 3: Ad-like auto-rejects (any one = REJECT)
- **R1:** the site/discount is the subject of any character's line.
- **R2:** a character asks or answers "how is it so cheap" (method handoff).
- **R3:** a character models conversion ("gonna try it").
- **R4:** FLEX-only (object + price, no conflict, mishap or reaction).
- **R5:** receipt-first, *and* the narrator is not at fault, *and* there is no story beat on the hook slide.
- **R6:** a visible zero/low tip or other unintended villain-narrator ledger (unless fairness is the intended mechanic).
- **R7:** the premise asserts a real public price/promo/trend not marked NEEDS-RESEARCH.
- **R8:** the premise is presented as a real event.
- **R9:** a sequel that only continues the object.

## Part 4: Forced-premise rejects (the story feels engineered to reach the product)
- **FP1:** the object is irrelevant to the violation but inserted anyway (an object that could be deleted without changing anything AND is high-desire = a product placement smell).
- **FP2:** the counterpart's behaviour exists only to set up the order.
- **FP3:** more than one coincidence is needed.
- **FP4:** the stakes are explained in an overlay instead of shown.


---
## Family D force checks (Mon 2026-10-05)
Apply in addition to Family I checks when `family_request=D`:
1. **Outcome image:** would a stranger want this photo without any caption? (D-OUTCOME-FIRST)
2. **Gap without story:** is there an accessibility/method/utility gap that is not interpersonal?
3. **Saveability:** is there a map, steps, board, checklist, or container structure worth keeping?
4. **Native proof:** imperfect real setting (not seamless catalog)?
5. **No-drama survival:** delete cast conflict — still works?
6. **Anti-sludge:** delete brand logos — still works?
7. **Anti-fake-promo:** any public shelf price+deadline claim? If yes and not a real public promo we control → REJECT
8. **Copy-distance:** not a plot clone of D-FD11 boo basket / D-FD12 Aldi fridge / D-FD01 dish list

Force score suggestion (Family D): outcome(0–2) + gap(0–1) + save(0–1) + proof(0–1) + no-sludge(0–1) + no-fake-promo(0–1) + distance(0–1) → FORWARD ≥6.
