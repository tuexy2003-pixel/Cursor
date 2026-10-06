---
name: Synthetic story generator
description: >-
  Use when MyDashPerks needs original FICTIONAL/STAGED carousel premise cards.
  It invents characters, relationships, mistakes and situations by recombining
  abstract viral mechanics and psychology patterns from the viral-story-learning
  pattern bank, never by copying plots. Outputs premise cards only (no
  storyboards, dialogue, prices or amounts). Cards feed the existing
  commercial-aware-synthesis stage as labeled staged gravity without changing
  any protected skill or gate.
---
# Synthetic story generator

## When to use
- The user asks for new story or desire/utility premises.
- A scout run produced thin gravity and fictional premises are wanted.

Do not use it for research questions (trends, prices, comments, performance). Those stay in RESEARCH mode with the existing scouts.

## Hard rules
1. **Label.** Every card says `LABEL: FICTIONAL/STAGED`. Never present an invented event as researched or real.
2. **Never invent research facts.** If a premise needs one (real price, current trend, retailer promo, comment behavior), write `NEEDS-RESEARCH: <fact>` and leave the value empty.
3. **Mechanics yes, plots no.** Never reuse an exemplar's dialogue, names, amounts, objects, sequence, relationship configuration, joke or ending.
   - Run the copy-distance check in `ORIGINALITY_AND_FORCE_CHECK.md`. Pass at ≥4. Any reused line/name/amount/joke/object detail fails.
   - Burned names: Dre, Kai, Malik, Terrence, Jalen, Miles, Cole, Nate, Omar, Tori, Eli R., Jay, Mira, Toni, Cam.
   - Burned kits:
     - kind delivery driver hides the item
     - freezer-chicken / "handled" rule-defiance couple
     - driver asks how the order is so cheap
4. **Premise cards only.** No storyboard, dialogue, prices, amounts, retailer choice or discount value unless a later request asks. Amount and economic-boundary work belongs to commercial-aware-synthesis.
5. **Commercial position** is one of `ABSENT`, `ARTIFACT` or `OUTCOME-MEANS`. Never `CENTER`. No character mentions the site or discount, or asks or answers "how is it so cheap".
6. **Keep the families separate.** Family I (interpersonal/event) needs a viewer job that survives deleting the discount. Family D (desire/utility) needs an identity constraint + an attainable, savable outcome. Hybrids name a primary family.
7. **Protected skills are read-only.** Do not edit, restate as new rules, or bypass:
   - commercial-aware-synthesis, V1.1/V1.2
   - NO TRANSITION
   - Gate 1/2A/2B
   - Campaign Salience, Desire/Utility
   - Live Heat, Object & Culture, Story & Conflict
   - Production QA, Adaptation Blitz
   The force score below is an internal self-check, not a pipeline gate.

## Pattern bank (read before generating)
All in `/workspace/creative-pipeline/shared/research/viral-story-learning/`:
- `VIRAL_STORY_MECHANIC_TAXONOMY.md`: mechanic codes (E-…, D-…, G-…) with swap tests.
- `VIRAL_PSYCHOLOGY_PATTERN_BANK.md`: PSY-01…PSY-15 (when it works / needs / kills / false positives).
- `WINNER_LOSER_CONTRAST_LIBRARY.md`: why similar surfaces won or lost.
- `SYNTHETIC_STORY_GENERATION_GRAMMAR.md`: slots A–I, combination rules, originality operators.
- `ORIGINALITY_AND_FORCE_CHECK.md`: copy-distance, force F1–F9, auto-rejects R1–R9, forced-premise FP1–FP4.
- `VIRAL_CREATIVE_EXAMPLE_CARDS.md`: exemplars for copy-distance comparison.

## Procedure
1. Read the inputs: family request, optional object/domain hint, account lane, recent posts (for novelty), count.
2. For each premise:
   1. **Mechanic.** Pick a PRIMARY mechanic, then ≤2 SECONDARY from a different exemplar lineage.
   2. **Story shape.** Pick a cast role not burned for that mechanic. Then set the violation, the info asymmetry (hook → middle → reveal), a proof type that answers the *story's* question, and an optional unmentioned residual question.
   3. **Object last.** If the object hint can only be inserted (forced), reject the hint and say why.
   4. **Surface path.** 2–4 native surface types, one per beat.
   5. **Commercial position.**
   6. **Engines.** Name the two campaign-independent engines in protected vocabulary: judgment / outcome desire / open question / proof demand / method gap.
   7. **Self-checks.** Run the no-discount test, copy-distance, force score and auto-rejects.
3. Output FORWARD cards (force ≥7, copy-distance ≥4, no auto-reject). Add REWORK cards with an originality operator, and a reject log.
4. Hand FORWARD cards to commercial-aware-synthesis as `gravity_source: FICTIONAL/STAGED`. Do not run gates, choose amounts, or storyboard here.

## Card schema
```
ID: SSG-<YYYYMMDD>-<n>
LABEL: FICTIONAL/STAGED
FAMILY:
PRIMARY MECHANIC / SECONDARY:
PSYCH PATTERNS:
CAST:
VIOLATION / TENSION:
INFO ASYMMETRY (hook → middle → reveal):
PROOF TYPE:
RESIDUAL QUESTION:
SURFACE PATH (types only):
COMMERCIAL POSITION:
OBJECT ROLE + REPLACEABILITY:
VIEWER JOB:
NO-DISCOUNT TEST:
CAMPAIGN-INDEPENDENT ENGINES:
NEAREST EXEMPLARS + COPY-DISTANCE:
FORCE SCORE + VERDICT:
RISKS:
NEEDS-RESEARCH:
```

## Known limits
- **The rubric is in-sample.** It was learned from 2 own winners and 4–5 own losers. Re-weight after the next 10 posted results.
- **Family D evidence is thin.** Desire/utility media is not on disk, so treat D cards as lower confidence.
