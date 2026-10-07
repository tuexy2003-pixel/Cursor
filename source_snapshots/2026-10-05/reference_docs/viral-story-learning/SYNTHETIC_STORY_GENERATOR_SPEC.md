# SYNTHETIC STORY GENERATOR: DESIGN SPEC

Built Mon 2026-10-05 ET. **Status: design + skill draft. NOT installed** (the executor has no UpdateSkill tool; see FINAL_REPORT §30).

## 1. Purpose
Invent ORIGINAL fictional/staged premise cards by recombining *mechanics and psychology patterns* learned from the corpus. Plots are never copied.

It replaces the retired direction of finding real co-located stories online (SER co-location is STOPPED).

## 2. Modes and labels
- **CREATIVE GENERATION mode (this generator):**
  - It may invent characters, relationships, mistakes, arguments, delivery/return/gift situations.
  - Every card carries `LABEL: FICTIONAL/STAGED`.
- **RESEARCH mode (never inside this generator):**
  - Trends, prices, comment behavior, and performance are never invented.
  - Any premise element that needs a real-world fact is tagged `NEEDS-RESEARCH: <fact>` and handed to the existing scouts. Those scouts are protected and unchanged.

## 3. Inputs
- **Required:** `family_request`: `I` (interpersonal/event), `D` (desire/utility), or `ANY`.
- **Optional:**
  - `object_hint`: none / category / specific object. A hint only; the generator may reject it as forced.
  - `domain_hint`: food, electronics, beauty, fashion, home, gifts, school, work, pets, travel.
  - `account_lane`: e.g. Sarah/Brooke = electronics, Maria = food/couples. Lane constraints come from `SYSTEM_PLAYBOOK.md`.
  - `recent_posts`: list of recent primary mechanic + role pairs, used for the novelty check F8.
  - `count`: premises requested. Default 6.
- **Reference artifacts read by the generator (read-only), all in `shared/research/viral-story-learning/`:**
  - `VIRAL_STORY_MECHANIC_TAXONOMY.md`
  - `VIRAL_PSYCHOLOGY_PATTERN_BANK.md`
  - `WINNER_LOSER_CONTRAST_LIBRARY.md`
  - `SYNTHETIC_STORY_GENERATION_GRAMMAR.md`
  - `ORIGINALITY_AND_FORCE_CHECK.md`
  - `VIRAL_CREATIVE_EXAMPLE_CARDS.md` (used for copy-distance comparison)

## 4. Algorithm
1. **Family split.** Decide I or D per slot. Never blend the two into one engine.
2. **Mechanic draw.** Choose a PRIMARY mechanic from the taxonomy (Family I: section A; Family D: section C). Then choose ≤2 SECONDARY mechanics from a *different* exemplar lineage.
3. **Cast and violation.** Choose a counterpart role not burned for that mechanic, then the violation/tension (grammar Slots A and C).
4. **Information asymmetry, proof, residual question** (Slots E–G).
5. **Object last.** If `object_hint` is given, test fit:
   - If the object can only be inserted (forced-premise FP1), reject the hint and record why.
   - Otherwise assign the object a role and check replaceability.
6. **Surface path** (types only, 2–4 surfaces; Slot H).
7. **Commercial position** (Slot I): ABSENT, ARTIFACT, or OUTCOME-MEANS. Never CENTER.
   - The generator does **not** choose amounts, retailers, or discount values.
   - Economic boundary work belongs to commercial-aware-synthesis, which is protected and unchanged.
8. **Self-checks** (`ORIGINALITY_AND_FORCE_CHECK.md`):
   - copy-distance against named exemplars plus the default set
   - force score F1–F9
   - auto-rejects R1–R9
   - forced-premise checks FP1–FP4
9. **Output.**
   - Premise cards for FORWARD results.
   - REWORK cards with the suggested originality operator.
   - A reject log with reasons.
10. **No storyboards, dialogue, prices, or real names** unless a later request asks for them.

The force score is a generator-internal advisory self-check. It is NOT a new pipeline gate, consistent with the protected rule "Do not create a downstream viral gate."

## 5. Output: premise card schema
```
ID: SSG-<date>-<n>
LABEL: FICTIONAL/STAGED
FAMILY: I | D | HYBRID(I-primary|D-primary)
PRIMARY MECHANIC / SECONDARY:
PSYCH PATTERNS: (PSY codes)
CAST: narrator + <role> [+ bystander]
VIOLATION / TENSION:
INFO ASYMMETRY (hook → middle → reveal):
PROOF TYPE (belongs to which story question):
RESIDUAL QUESTION (unmentioned) | none:
SURFACE PATH (types only):
COMMERCIAL POSITION: ABSENT | ARTIFACT | OUTCOME-MEANS
OBJECT ROLE + REPLACEABILITY:
VIEWER JOB (one line):
NO-DISCOUNT TEST: PASS/FAIL + why
CAMPAIGN-INDEPENDENT ENGINES (named in protected vocabulary: judgment / outcome desire / open question / proof demand / method gap):
NEAREST EXEMPLARS + COPY-DISTANCE (each):
FORCE SCORE (F1..F9) + verdict:
RISKS:
NEEDS-RESEARCH:
```

## 6. Proposed pipeline position (protected pipeline NOT rewritten)
The protected `commercial-aware-synthesis` pipeline runs:
1. Scout reality
2. Map human/desire gravity
3. Commercial affordance map
4. Synthesis
5. Internal filter
6. Adversarial research
7. Existing gates
8. Concept lock
9. Storyboard
10. Reference/asset acquisition
11. Production
12. QA

**Proposal:** the generator sits *beside* steps 1–2 as an additional, labeled source of human/desire gravity + mechanic candidates.

```
[Story & Conflict / Live Heat / Object & Culture scouts]  (RESEARCH, protected)
                                     \
                                      → step 2 gravity pool → step 3 affordance map → step 4 synthesis → … existing gates (unchanged)
                                     /
[synthetic-story-generator]  (CREATIVE, new, FICTIONAL/STAGED premise cards)
```

- **Handoff:** premise cards enter step 2 as `gravity_source: FICTIONAL/STAGED` candidates.
  - commercial-aware-synthesis does all affordance, boundary, transition and NO TRANSITION classification, engine naming, and economic-job work exactly as written.
  - Gate 1/2A/2B, Campaign Salience, Desire/Utility, Production QA and Adaptation Blitz are unchanged.
- **Consistency check with protected rules (read-only review):**
  - CAS "two campaign-independent engines" ↔ the generator's NO-DISCOUNT test and engine naming. Compatible.
  - CAS "promotion-first firewall" ↔ auto-rejects R1–R4 and FP1–FP2. Compatible.
  - CAS "Do not add conflict… merely to complete the stack" ↔ the generator invents conflict *as the premise's gravity*, before any commerce. It never invents conflict to make a discount matter. Compatible in spirit, but see the open question below.

## 7. OPEN QUESTION for the user (STOP + ask; not acted on)
CAS step 1 reads "Scout reality". Formally accepting FICTIONAL/STAGED gravity cards as step-2 input may need a wording change inside the protected `commercial-aware-synthesis` skill. **I did not edit it.**

Options for the user:
- (a) Keep CAS as is. Treat generator cards as "staged gravity" that still pass CAS unchanged. This is the default assumed here.
- (b) Authorize a one-line CAS amendment.

## 8. Failure modes and mitigations
- **Mechanic mode collapse** (always rule-defiance couples): novelty check F8 plus the burned role list.
- **Generator drift toward the ad:** auto-rejects; commercial position CENTER is not allowed.
- **Synthetic comments mistaken for evidence:** the generator never outputs comments. Predicted reactions are only ever labeled `SYNTHETIC (predicted)` in analysis docs.
- **Over-fitting to 2 winners:** the corpus has only 2 own WIN posts. The rubric is in-sample (see the blind-test caveat). Re-weight after the next 10 posted results.


---
## Family D calibration note (Mon 2026-10-05 — companion update; SKILL.md unchanged)
- Desire/utility evidence is no longer metrics-only. See `family-d-expansion/FAMILY_D_CARDS.md` (D-FD01–12 strong; D-FW01–05 controls).
- **Family D confidence: MEDIUM** for outcome→steps/map carousels and constraint+abundance shells; still avoid D-SCARCE-REAL-DEAL.
- When generating Family D: require D-OUTCOME-FIRST + (D-ASPIRATION-STEPS or D-MAP-SLIDE or D-ABUNDANCE-UNDER-CONSTRAINT) + native proof. Do not paste interpersonal conflict to rescue weak desire.
- O7-class OUTCOME-MEANS handoffs should cite slide-order from D-FD01/03/09/12 and remain organic-only unless a real existing commercial cause exists.
