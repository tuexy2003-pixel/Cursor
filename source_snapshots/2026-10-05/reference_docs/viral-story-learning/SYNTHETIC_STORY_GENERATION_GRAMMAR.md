# SYNTHETIC STORY GENERATION GRAMMAR

CREATIVE-GENERATION MODE. Built Mon 2026-10-05 ET.

This is how to invent ORIGINAL fictional/staged premises by combining *mechanics*, not plots.

**Every output is labeled `FICTIONAL/STAGED`.** Invented events are never presented as researched. Research-mode facts (trends, prices, comments, performance) are never invented. If a premise needs one, it is marked `NEEDS-RESEARCH: <what>`.

## 0. The two families stay separate
- **Family I, INTERPERSONAL/EVENT STORY:** a viewer job (judge / wonder / complicity / kindness) that exists *without* the discount. Commerce enters only as a native artifact (order, payment, notification, receipt line) that serves the story.
- **Family D, DESIRE/UTILITY:** an identity constraint + an attainable, savable outcome image. No interpersonal conflict is required. Commerce enters as the outcome's means.
- **Hybrid is allowed** only if one family is clearly primary and the other is secondary.

## 1. Components (pick one or more from each slot)

**SLOT A: Cast (relationship geometry).** Narrator + ONE counterpart, optionally one bystander.
- Counterpart roles:
  - partner
  - roommate
  - parent
  - sibling
  - grandparent
  - coworker
  - manager
  - ex
  - neighbor
  - landlord
  - group chat
  - stranger-service-worker (driver, cashier, maintenance, receptionist)
  - kid
  - teacher/coach
  - online buyer/seller
- Rule: rotate away from the roles already burned in the same mechanic. Kind-dasher is burned (P01, P05, P06). Couple-food-rule is heavily used (P02, P04, P08, U03, U04, P11).

**SLOT B: Mechanic (from the taxonomy).** One PRIMARY + at most two SECONDARY. Primary must be a story mechanic (Family I) or a D-mechanic (Family D).

**SLOT C: Violation / tension source.**
- broken rule
- outrageous ask
- caught artifact
- mishap
- betrayal
- absurd condition
- identity contradiction
- unearned kindness
- ledger imbalance

**SLOT D: Stakes object (optional).** Role options:
- stakes amplifier
- defiance artifact
- incriminating evidence
- gift
- outcome image
- none

Replaceability check: if the object can be swapped and the viewer job survives, it is correctly subordinate.

**SLOT E: Information asymmetry.** Who knows what at the hook / middle / reveal:
- viewer > counterpart (complicity)
- counterpart > narrator (reveal)
- viewer = narrator, withheld (outcome desire)

**SLOT F: Proof type (must belong to the story):**
- photo of the outcome
- notification
- order screen as act-proof
- payment screen
- history list
- location/timestamp
- selfie reaction

**SLOT G: Residual open question (optional, never mentioned):** a visible anomaly that viewers raise themselves. The buried number is ONE option, not mandatory.

**SLOT H: Surface path (2–4 native surfaces, one per beat).**
- iMessage / SMS
- lock screen
- Notes
- Snapchat
- order complete
- receipt
- payment app
- camera roll / Photos
- search bar
- product page
- selfie + overlay
- meme
- reaction

**SLOT I: Commercial position.** Choose one:
- `ABSENT` (pure story test)
- `ARTIFACT` (native order/payment line that the story needs for its own reason)
- `OUTCOME-MEANS` (Family D)

Never `CENTER`.

## 2. Combination rules
1. **Mechanic first, object last.** Generate cast + mechanic + violation + asymmetry before choosing any object.
2. **Viewer-job test:** write one line, "The viewer's job is to ___." If it reads "notice the discount", REJECT.
3. **No-discount test:** delete Slot I. If the premise collapses, REJECT (Family I) or reclassify as Family D (it must then pass D tests).
4. **One absurd detail max** (PSY-10).
5. **No character may ask or answer the method question** (E-METHOD-HANDOFF ban).
6. **The hook must promise only what the premise delivers** (C3 lesson).
7. **Sequels continue an unresolved question or a new conflict with the same cast.** Never just the object (C2 lesson).
8. **Proof belongs** (G-PROOF-BELONGS).
9. **Narrator owns some fault** when the order or receipt is early (C5 lesson).
10. **Combine at least two mechanics from different winners' families.** Never combine the full mechanic set of a single exemplar, because that is plot cloning.

## 3. Family D grammar (desire/utility)
Updated Mon 2026-10-05 after `family-d-expansion/` (D-FD01–12). **A story is not necessary** when all five are present: desirable/recognizable outcome + visual/cultural want + accessibility/method/utility gap + native proof + replication desire.

- **Template (abstract):** `[OUTCOME-FIRST image]` + optional `[identity constraint]` + `[savable structure: list / steps / map / before-after / container grid]` + optional `[withheld means]` + optional `[total that invites audit]`.
- **Slot order that matched winners:**
  1. Outcome / desire image early (D-OUTCOME-FIRST)
  2. Method/map/process mid (D-ASPIRATION-STEPS / D-MAP-SLIDE)
  3. Native proof continuous (containers, POV plate, fridge stock, in-situ object, used kit)
  4. Totals late or mid-board if used (D-TOTAL-INVITES-AUDIT)
- **Constraints (examples, not a closed list):**
  - moving / student / new parent / first apartment / post-breakup / long shift / small kitchen / one paycheck left / dorm / travel / no-drill lease / eight-minute bathroom
- **Outcomes:**
  - full fridge / glam look / cozy room / gift basket / week of meals / outfit set / self-care night / cleaning reset / desk corner "done"
- **Tests:**
  1. **No-drama test:** delete every interpersonal cast member. If the viewer job (want/save/audit/replicate) survives → Family D OK.
  2. **No-discount test:** delete any deal. If outcome+gap survive → OK.
  3. **Anti-sludge test:** if removing brand logos kills the post → REJECT (D-FW01 class).
  4. **Anti-flex test:** if removing constraint AND method leaves only object+price → REJECT (P07/D-FW05 class).
- **Prohibited:** asserting a public retailer price or promo that is not real (D-SCARCE-REAL-DEAL / D-FW05). Do **not** invent fake interpersonal drama to rescue a weak D premise — either strengthen D engines or switch to Family I for real.
- **Calibration exemplars on disk:** D-FD01–12 in `family-d-expansion/FAMILY_D_CARDS.md`.

## 4. Originality operators (to move away from exemplars)
- **Role inversion:** the kind party becomes the narrator, or the authority becomes the rule-breaker.
- **Domain transplant:** move the mechanic into a different life domain (work, school, pets, fitness, beauty, home, travel).
- **Surface transplant:** move the reveal from chat to lock screen / Notes / Photos memory / search history.
- **Stakes inversion:** the object at risk is mundane but emotionally precious (grandma's leftovers, a pet's medication) instead of expensive.
- **Asymmetry flip:** the counterpart knows the secret and the narrator is the one in the dark.

## 5. Output shape (premise card only)
Fields:
- `ID`
- `LABEL: FICTIONAL/STAGED`
- `FAMILY`
- `PRIMARY MECHANIC`
- `SECONDARY`
- `PSYCH PATTERNS`
- `CAST`
- `VIOLATION`
- `INFO ASYMMETRY`
- `PROOF TYPE`
- `RESIDUAL QUESTION`
- `SURFACE PATH (types only)`
- `COMMERCIAL POSITION`
- `OBJECT ROLE + REPLACEABILITY`
- `VIEWER JOB`
- `NO-DISCOUNT TEST`
- `NEAREST EXEMPLARS + COPY-DISTANCE`
- `FORCE SCORE`
- `RISKS`
- `NEEDS-RESEARCH`

**Not included:** no dialogue, no exact prices, no storyboards, no names of real people. Generic placeholders only ("partner", "roommate").
