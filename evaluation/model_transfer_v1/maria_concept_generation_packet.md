# Creative OS provider packet
PROVIDER_EXECUTION: NOT_IMPLEMENTED
Use only this packet. Do not search the web. Do not mutate stored creative truth.
COMPILER: context-compiler-0.3.0
AS_OF: 2026-10-06T20:37:02.666607+00:00
STAGE: CONCEPT_GENERATION

## TASK
Generate 5 NEW staged short-form carousel concepts appropriate for this account
using the current creative operating system.

Requirements:
- new concepts, not copies of benchmarks
- story-native commerce
- roughly 15–20 life-world where current account or program policy says so
- believable human causality
- multiple potential comment doors
- do not pad baskets for economics
- commerce and economic discovery should follow current policy
- do not search the web in this manual evaluation
- flag research needed instead

Do not create a Creative or a StoryLock. These concepts are proposals for human review.
Task id: e6c5f123-5025-45e4-97fd-a2e5fa0e91fc
Stage: CONCEPT_GENERATION
Status: CONSUMED
Expected output: CONCEPT_GENERATION
Constraints:
{}
Input refs:
{}

## OUTPUT CONTRACT CONCEPT_GENERATION
Return ConceptGenerationResult JSON only. Each concept is a proposal for human review. It is not a StoryLock. Leave unknown fields null. Do not copy holdout or benchmark stories.
{
  "$defs": {
    "ConceptDraft": {
      "properties": {
        "action_trigger": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Action Trigger"
        },
        "commerce_relation": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Commerce Relation"
        },
        "expected_consequence": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Expected Consequence"
        },
        "family": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Family"
        },
        "hook_direction": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Hook Direction"
        },
        "human_event": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Human Event"
        },
        "payoff": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Payoff"
        },
        "premise": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Premise"
        },
        "primary_comment_door": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Primary Comment Door"
        },
        "proof_surface_direction": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Proof Surface Direction"
        },
        "research_needed": {
          "items": {
            "type": "string"
          },
          "title": "Research Needed",
          "type": "array"
        },
        "reveal": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Reveal"
        },
        "risks": {
          "items": {
            "type": "string"
          },
          "title": "Risks",
          "type": "array"
        },
        "secondary_comment_doors": {
          "items": {
            "type": "string"
          },
          "title": "Secondary Comment Doors",
          "type": "array"
        },
        "stakes": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Stakes"
        },
        "title": {
          "title": "Title",
          "type": "string"
        },
        "viral_texture_opportunities": {
          "items": {
            "type": "string"
          },
          "title": "Viral Texture Opportunities",
          "type": "array"
        },
        "why_it_fits_account": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Why It Fits Account"
        }
      },
      "required": [
        "title"
      ],
      "title": "ConceptDraft",
      "type": "object"
    }
  },
  "properties": {
    "concepts": {
      "items": {
        "$ref": "#/$defs/ConceptDraft"
      },
      "title": "Concepts",
      "type": "array"
    }
  },
  "required": [
    "concepts"
  ],
  "title": "ConceptGenerationResult",
  "type": "object"
}

## GLOBAL INVARIANTS
### principles-a-01 (GLOBAL INVARIANT)
version 32aa5351-805f-454f-8b0e-5064fb8fc8e7 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-01; retained regardless of token budget
The latest human-approved STORY_LOCK wins for story-specific values. Superseded assets are marked STALE; files are not deleted or rewritten.

### principles-a-02 (GLOBAL INVARIANT)
version c1dce379-8a04-4702-9f78-7f92a077cae9 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-02; retained regardless of token budget
An explicit human correction beats any skill default, until the skill is updated.

### principles-a-03 (GLOBAL INVARIANT)
version 173ff17a-478e-4d8a-88ce-266afb620b55 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-03; retained regardless of token budget
Proof boundary: a proof surface proves only what it literally shows. It cannot invent the actor's intent, location, payment causality or a retailer promotion.

### principles-a-04 (GLOBAL INVARIANT)
version 478c3159-0a02-48c4-a864-a0ea58cf32e7 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-04; retained regardless of token budget
Research mode never invents evidence. Staged/creative economics are labeled FICTIONAL/STAGED and never presented as a real retailer promo.

### principles-a-05 (GLOBAL INVARIANT)
version 7d2c61db-ee98-4454-a20d-aeaed4b37b8b priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-05; retained regardless of token budget
Reference-first production: when a suitable real base exists, edit it (smallest localized edit) and do not freehand-reconstruct retailer UI.

### principles-a-06 (GLOBAL INVARIANT)
version c2f0abae-2da5-43b2-8a33-2c49bf62485a priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-06; retained regardless of token budget
Never silently compress or squeeze native UI rows to fit content. If it doesn't fit, choose another real base or a natural scroll state.

### principles-a-07 (GLOBAL INVARIANT)
version 39b2ded4-048b-43d1-ba78-9ad2c530d085 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-07; retained regardless of token budget
Story-specific visible dates, times and weekdays come from the continuity ledger, not from the reference image.

### principles-a-08 (GLOBAL INVARIANT)
version dafd8c70-dd09-48a4-9fd0-c7ab26310f9b priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-08; retained regardless of token budget
Cross-slide congruency: no impossible state or time transitions (for example "tomorrow" followed by the party already happening with no time change).

### principles-a-09 (GLOBAL INVARIANT)
version 6394e18f-5cdc-4ffb-95e5-2cd1765f5a63 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-09; retained regardless of token budget
Discount-headroom firewall: never add an expensive item only to enlarge the subtotal or discount. Items must be story-motivated.

### principles-a-10 (GLOBAL INVARIANT)
version 0077238d-b1b0-4aee-aef5-ad5599514475 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-10; retained regardless of token budget
Re-edits start from the original base, never from a drifted or degraded output.

### principles-a-11 (GLOBAL INVARIANT)
version 93eecee7-6bf8-4cef-92fa-4b01adeb57a7 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-11; retained regardless of token budget
Any real object added to an image is edited in using a real photo of that exact object as a reference.

### principles-a-12 (GLOBAL INVARIANT)
version 9ea10bd0-62fe-4cd8-8d66-aa1201861bc5 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-12; retained regardless of token budget
Real products use the current generation and live price, verified before lock.

### principles-a-13 (GLOBAL INVARIANT)
version 265197d7-7aa1-488a-812f-d6609cf24e3f priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-13; retained regardless of token budget
Rights: personal or unknown-rights images (Pinterest pins) are REFERENCE ONLY and their pixels are never shipped. Only CLEARED images may be a BASE.

### principles-a-14 (GLOBAL INVARIANT)
version fa5aebf9-5933-4a3c-a317-278c592d23e4 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-14; retained regardless of token budget
Never send messages, place orders or post without explicit human approval. DoorDash carts are referenced, never checked out.

### principles-a-15 (GLOBAL INVARIANT)
version 2c4c62a2-68d5-4e9e-9bcb-d086ba176773 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-15; retained regardless of token budget
The money path appears only as the native "mydashperks.com Discount" line on the order surface. It never appears in chat bubbles, never on S1, and never as a savings slide.

### principles-a-16 (GLOBAL INVARIANT)
version fa373c64-bebe-452d-a3f9-817375cc01c6 priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-16; retained regardless of token budget
Frozen architecture (V1.2, CAS, Gates 1/2A/2B, campaign salience, Desire/Utility gate, scouts, Live Heat, firewall) is not modified without explicit authorization.

### principles-a-17 (GLOBAL INVARIANT)
version d60ab077-cfb5-4540-86c1-f028fb77f2eb priority authoritative authority hard invariant
Included because: resolved GLOBAL INVARIANT for principles-a-17; retained regardless of token budget
No burned real names or handles of private people. Amounts and clocks are internally consistent.

### principles-b-01 (GLOBAL HEURISTIC)
version 14c0120d-5829-403f-be2d-f34097e9ebf6 priority scope=4;kind=1;stage=1;order=7;code=principles-b-01 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-01
Use the hook-presentation router: cropped full thread, lock-screen, preview card, peek or thread plus floating hook. Peek only when the conversation fills the card.

### principles-b-02 (GLOBAL HEURISTIC)
version 9c1c0857-89f2-427a-9ff7-a82d8ef86e1e priority scope=4;kind=1;stage=1;order=8;code=principles-b-02 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-02
Avoid dead space on S1.

### principles-b-03 (GLOBAL HEURISTIC)
version 9f9f99c8-9b3c-4ba0-b4ba-a7d835162480 priority scope=4;kind=1;stage=1;order=9;code=principles-b-03 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-03
0–3 secondary micro-details per slide, with quality over count.

### principles-b-04 (GLOBAL HEURISTIC)
version 57e47e38-5d8c-46fa-8e95-a1f634392da6 priority scope=4;kind=1;stage=1;order=10;code=principles-b-04 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-04
Commerce is usually a secondary discovery. Family D can lead with desire/method instead.

### principles-b-05 (GLOBAL HEURISTIC)
version eb4ac548-22ca-48a3-a778-220f0def0c8a priority scope=4;kind=1;stage=1;order=11;code=principles-b-05 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-05
Camera-roll payoff: visual search first (Pinterest short queries) before any generation.

### principles-b-06 (GLOBAL HEURISTIC)
version 19baffb7-8f82-44e6-986b-822a13b4e8c7 priority scope=4;kind=1;stage=1;order=12;code=principles-b-06 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-06
S1 often uses a native TikTok floating hook. The hook must add new context, never restate a bubble.

### principles-b-07 (GLOBAL HEURISTIC)
version 92aa2f2f-7c67-460e-b9ac-ca7865b2489c priority scope=4;kind=1;stage=1;order=13;code=principles-b-07 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-07
Story-led concepts should usually work without the economics.

### principles-b-08 (GLOBAL HEURISTIC)
version 22705ce8-d775-4e9b-993b-699105f47459 priority scope=4;kind=1;stage=1;order=14;code=principles-b-08 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-08
A completed order can open a carousel. The notification-then-receipt opener is not required.

### principles-b-09 (GLOBAL HEURISTIC)
version e5708e32-c49a-4824-925d-d9e660153271 priority scope=4;kind=1;stage=1;order=15;code=principles-b-09 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-09
Keyboard-up Messages is an option, not a rule.

### principles-b-10 (GLOBAL HEURISTIC)
version 5cb480ca-1bad-4734-8928-139ba08d9dd7 priority scope=4;kind=1;stage=1;order=16;code=principles-b-10 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-10
Temporal compression is fine when it's plausible.

### principles-b-11 (GLOBAL HEURISTIC)
version 63118b4d-03eb-49ad-9656-57a80148cdba priority scope=4;kind=1;stage=1;order=17;code=principles-b-11 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-11
Use about three slides: hook, proof, payoff.

### principles-b-12 (GLOBAL HEURISTIC)
version 1c3d0df0-3853-4475-8d0e-b81542249389 priority scope=4;kind=1;stage=1;order=18;code=principles-b-12 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-12
Make aspect changes through the image editor, not by crop or stretch.

### principles-b-13 (GLOBAL HEURISTIC)
version 51d947c9-0942-4701-a6b5-944191a6f5f0 priority scope=4;kind=1;stage=1;order=19;code=principles-b-13 authority heuristic
Included because: resolved GLOBAL HEURISTIC for principles-b-13
Prefer user-supplied screenshots over the reference bank, over organic screenshots, over marketing images, over generation.

## PROGRAM POLICIES
### principles-c-01 (PROGRAM PREFERENCE)
version ff8cbbe1-3168-484b-b00f-990bd2d192d0 priority scope=3;kind=0;stage=1;order=0;code=principles-c-01 authority preference
Included because: resolved PROGRAM PREFERENCE for principles-c-01
The audience is the 15–20 phone life-world: high school or first-year college, parents, siblings, friends, group chats, Target/Sephora. Avoid adult gravity such as landlords, marketplaces and corporate settings.

### principles-c-02 (PROGRAM PREFERENCE)
version ef05bace-74ce-41ea-a0d9-be154f74190d priority scope=3;kind=0;stage=1;order=1;code=principles-c-02 authority preference
Included because: resolved PROGRAM PREFERENCE for principles-c-02
Account lanes: Maria covers food and couples (e.g. Dre). Sarah and Brooke cover electronics.

### principles-c-03 (PROGRAM PREFERENCE)
version 3fdabe19-b5e5-4c58-b5b7-e5edc3e26c5c priority scope=3;kind=0;stage=1;order=2;code=principles-c-03 authority preference
Included because: resolved PROGRAM PREFERENCE for principles-c-03
Ecosystems are TARGET and DOORDASH only.

### principles-c-04 (PROGRAM PREFERENCE)
version 67354a96-2bdf-415e-af5c-364b0990d64d priority scope=3;kind=0;stage=1;order=3;code=principles-c-04 authority preference
Included because: resolved PROGRAM PREFERENCE for principles-c-04
Final format is 9:19.6 portrait (1206×2622 native, or about 851×1849). It is never 1080×1920 or 9:16.

### principles-c-05 (PROGRAM PREFERENCE)
version f03f3544-3a7f-43cf-9f77-c6aff5c18e6d priority scope=3;kind=0;stage=1;order=4;code=principles-c-05 authority preference
Included because: resolved PROGRAM PREFERENCE for principles-c-05
Tone: casual and lowercase where natural, with emoji like 😭. No marketing, UI-doc or sitcom phrasing.

### principles-c-06 (PROGRAM PREFERENCE)
version 8a4918e2-4653-4f6b-bba5-cba6140769ba priority scope=3;kind=0;stage=1;order=5;code=principles-c-06 authority preference
Included because: resolved PROGRAM PREFERENCE for principles-c-06
Proven patterns (historical): overslept + Dasher + object outside; a couple fight + a dumb food total; a money ask + an unfair reason + proof.

### principles-c-07 (PROGRAM PREFERENCE)
version e7167694-cba4-4a56-8b76-077d59f1ee5e priority scope=3;kind=0;stage=1;order=6;code=principles-c-07 authority preference
Included because: resolved PROGRAM PREFERENCE for principles-c-07
Dark-mode iOS 26 surfaces.

## SKILLS
### synthetic-story-generator role REQUIRED
version handoff-2026-10-05 id 5e5b7693-4b34-4aca-9902-2dc6bf7b98ed hash edebf6cee79e3df215c2681e3154c41a7bde57598dcd2910db80dda34f322e1b
Included because: required skill for stage CONCEPT_GENERATION
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


### commercial-aware-synthesis role REQUIRED
version handoff-2026-10-05 id 95b07559-0be2-4a37-9fbe-88d0ab9eb575 hash 822b9c18e1136a64932d423dc57048a5a7f35e86a08177a2ee2f13ea769dc5a0
Included because: required skill for stage CONCEPT_GENERATION
---
name: Commercial-aware synthesis
description: >-
  Use before the existing carousel gates, to compose a premise from human or
  desire gravity, a creative mechanic, and a commercial affordance recorded as
  an economic state boundary under variable promotional value up to $500,
  searching for two campaign-independent attention engines plus one qualitative
  economic job, without starting from a discount.
---
# Commercial-aware synthesis

## When to use
Before any existing gate. This stage composes a premise. It does not change Story-Led Gate 1, Gate 2A, Gate 2B, the Desire/Utility gate, campaign salience, transaction fidelity, the existing-promotion distinction, credibility, the promotion-first firewall, the internal-filter threshold, the early exits, the regression cases, or production rules.

## Pipeline
1. Scout reality.
When an input card is labeled `gravity_source: FICTIONAL/STAGED`, do not research whether the invented human event occurred; for `Scout reality`, research only the premise's factual surroundings (object desirability, culture/currentness, normal prices, retailer/transaction realism, and existing economic causes), while evaluating the fictional premise's creative strength through the normal downstream checks.
2. Map human and desire gravity.
3. Separately map commercial affordances as economic boundaries under the creative economic model.
4. Commercially aware creative synthesis.
5. Internal filter.
6. Adversarial research.
7. Existing applicable gates.
8. Concept lock.
9. Storyboard.
10. Reference and asset acquisition.
11. Production.
12. QA.

Do not generate a concept, run scouts, or choose a retailer, object, transaction, amount, or storyboard from this skill alone. Use the stage when a later request asks for origination.

## Creative economic model versus real-world fulfillment
Keep these apart.

**Creative economic model.** For creative ideation, MyDashPerks supplies variable promotional value from $0 up to $500. The system may test any amount at or below $500 as the economic variable in a fictional or staged commerce scenario. It must not default to $500. Its job is to find what amount, if any, crosses a meaningful boundary in the premise. The creative presentation may express that value through a staged commerce artifact, such as a discount or savings line, when that is the chosen fictional presentation.

**Real-world fulfillment model.** Separately researched reward-program mechanics, landing pages, Deals, delayed gift cards, affiliate paths, and site status. Those are fulfillment notes. They may inform later disclosure, landing-page, or offer-implementation decisions. They do not redefine the economic affordance used for creative synthesis, and they do not collapse the creative model during concept generation.

Do not classify a candidate as impossible merely because the literal external rewards program would not generate that exact retailer UI state. Do not report the creative model as proof of a real retailer integration. Research has not verified that MyDashPerks literally integrates with Target, DoorDash, or another retailer checkout.

Research may still verify normal product prices, normal basket sizes, normal consumer behavior, real objects, real cultural situations, existing promotions, transaction chronology, whether the amount is materially meaningful, and whether another ordinary mechanism already explains the outcome. Preserve metadata: staged presentation versus verified real-world retailer behavior.

## Commercial affordance map
Category-only labels are not enough. Access, choice, quantity or scale, quality, upgrade, timing, repetition, justification, and participation may appear as optional descriptive tags. They are not usable affordances by themselves.

A usable commercial affordance is an economic boundary or state transition under the creative economic model. Do not invent a boundary because a vocabulary entry exists. Do not begin an entry with a fixed campaign amount, a brand name, a coupon, a retailer, a conveniently expensive SKU, or the claim that people like saving money. Do not ask how to use $500. Ask what economic threshold separates outcome A from outcome B, then whether an amount at or below $500 can plausibly cross it. Prefer the smallest materially sufficient amount over maximizing promotional value.

### Required fields
For every proposed affordance record:

- Current state
- Real constraint
- Behavior or outcome without promotional value
- Boundary amount or range
- Smallest material amount likely to cross the boundary
- Behavior or outcome after crossing
- Why that is a qualitative change
- What already explains the change
- What would make the amount too small
- What would make the amount so large that it becomes unbelievable or destroys credibility
- Presentation mode
- Optional legacy tag

### Valid transition families
Use these as a compact working vocabulary, not boxes that must be filled:

- Excluded → able to participate
- Settling → preferred outcome
- Not enough → enough for the actual need
- Delayed → possible now
- One-time → repeatable
- Lower tier → meaningful upgrade
- Abandon → complete
- Forced substitute → exact needed thing

Other transitions are allowed only when they represent the same kind of genuine change in behavior, access, choice, scale, timing, participation, or achievable outcome.

### Non-transition
Explicitly mark NO TRANSITION — CHEAPER SAME OUTCOME whenever promotional value only lowers the total, improves the deal, increases savings, reimburses part of an already-decided purchase, makes an existing choice slightly more rational, or makes an existing argument numerically larger or smaller. Those entries do not enter synthesis as usable economic jobs.

### Existing-cause check
Before presenting a transition to synthesis, ask whether life, the category, another promotion, or the existing situation has already crossed or explained this boundary. If yes, the campaign cannot claim that transition merely because promotional value makes the same crossing cheaper. Examples of that failure shape: a personal ebook purchase that already provides delayed → now; pizza that already provides the wedding cost transformation; ribbon inflation that already explains a budget mum; return fees and fit uncertainty that already explain bracketing; medication that already explains a changed basket; thrift context that already explains cheapness.

A lower count of usable boundaries is acceptable. No usable economic boundary is a successful map output. Do not weaken the representation because few boundaries appear. That scarcity is diagnostic evidence about whether promotional value can cross real thresholds inside natural gravity.

## Synthesis
Hold three inputs apart: human or desire gravity, a creative mechanic, and a commercial affordance that survived the boundary map. Only this stage may combine them. Do not force economics into every human event. Do not choose the object or transaction because it maximizes promotional value. The object emerges because it expresses the intersection. The promotional value should intersect with existing gravity.

For a story, the human event must still hold if the campaign is removed. For desire or utility, the wanted or replicated outcome must still hold if the campaign is removed.

A commercial affordance is not campaign fit. It is only a hypothesis that promotional value of some amount at or below $500 could change an outcome in the staged premise. The boundary map supplies candidate economic jobs. Later research still has to verify normal prices, baskets, behavior, objects, existing promotions, chronology, materiality, residual economic space, credibility, and what those promotions actually explain. Transaction fidelity is judged for the staged scenario. The existing gates decide whether it works.

### Search objective
Do not stop at the first natural intersection, and do not stop because gravity and an affordance merely intersect.

While composing, actively search for an intersection that already contains at least two campaign-independent attention engines. The engines are judgment, outcome desire, open question, proof demand, and method gap.

- Judgment: the viewer can take a side, or recognize a real social position that implies one.
- Outcome desire: the object or result is wanted, absurd, useful, or recognizable with no price attached.
- Open question: the first information is incomplete, and a later fact can change what it meant. Extra beats are not an open question.
- Proof demand: the claim makes a specific artifact worth seeing, such as a receipt, a photo, or an order.
- Method gap: once the outcome is believed, the viewer still wants the how.

Those two engines must remain nameable if the campaign and its economics are completely removed. Prefer intersections where that stack is already present. Every engine must emerge from one coherent premise.

Engine count is a search objective, not a gate. Do not create a downstream viral gate. Thin intersections may still be recorded. Do not invent an engine to reach two. Do not add conflict, characters, emergencies, desirable objects, urgency, purchases, or exaggerated economics merely to complete the stack or to make promotional value matter.

If strong gravity has no natural commercial job, leave it organic-only. If a commercial affordance exists but only one campaign-independent engine is present, record a thin intersection and do not manufacture another. Only after synthesis does a candidate enter the same existing internal filter and the same existing gates.

### Economic job
After the two campaign-independent engines are named, assign the commercial affordance exactly one job:

- Create or amplify a method gap.
- Create or amplify proof demand.
- Create an outcome transformation.

The boundary map is what supplies the candidate job, including the smallest material amount likely to cross it. Synthesis still decides whether one naturally belongs with the gravity and the mechanic.

### Qualitative change
Amplify does not mean cheaper makes the argument stronger, a larger saving makes the object more desirable, a lower price makes an existing situation more dramatic, or economics raise the stakes numerically.

The economic job must produce a qualitative information-state change. A new unresolved how. A transaction artifact becomes specifically worth seeing or auditing. Or the economics materially change which outcome is reachable, chosen, scaled, upgraded, repeated, justified, or participated in.

If economics merely make an already-decided outcome cheaper, there is no economic job.

### Promotion independence
The economic job cannot also be counted as one of the two campaign-independent engines. The minimum structure is engine A, plus engine B, plus one economic job. It is not engine A, plus a discount, plus the same discount counted again.

## Promotion-first firewall
Reject synthesis when removing the campaign economics destroys the reason to watch or want the outcome, when the object exists only to provide discount headroom, when the human behavior was invented to justify a transaction, when the premise is only that a normally expensive thing is cheaper, when campaign branding is what creates the curiosity, or when an existing promotion already explains the relevant transformation.

A small existing promotion explains only what it actually explains. A category whose current cultural story is already aggressive discounting can still fail salience.

## Regression cases, do not reopen
Cheesecake Factory modified Cajun salmon: desire pass, transaction fidelity fail. Do not substitute the base salmon.
McDonald's Double Cheeseburger plus chocolate chip cookie: desire pass, transaction pass, economic materiality fail. Do not pad the basket.
Also still closed: the Cheesecake vow, the BYOMA campaign, migraine delivery, diaper-gift replenishment, and the wrong-door sandwich whose lesson is don't pay twice.

Early exits stay in force. The exact desired outcome must be expressible. Do not swap a base SKU for a modified outcome. Do not pad a small basket. Judge materiality on the natural transaction. Fail when a meaningful save consumes nearly all product value and leaves mostly fees. An artifact proves only what it visibly shows.


### adaptation-blitz-match role REQUIRED
version handoff-2026-10-05 id f0a2e950-377a-4db5-b71d-8dbec361cfa9 hash e61fa87711af3edac430a1a768e3ee21baa961390c8d901d5322ff8eba8b29e8
Included because: required skill for stage CONCEPT_GENERATION
---
name: Adaptation Blitz match
description: >-
  Use when choosing carousel finalists. Event evidence and object evidence stay
  separate. Gate 1, then Gate 2A or 2B, then campaign salience. Rank only
  stories whose campaign contribution is itself interesting. Neither origin
  ranks higher.
---
# Adaptation / Blitz match

## When to use
After commercial-aware synthesis, scout reports, or a source card, when choosing which concepts survive. This skill may invent the situation, then tests it. It does not acquire assets, assign surfaces, or produce images.

Upstream, and not a change to any gate: scout reality, map human and desire gravity, separately map commercial affordances, then commercial-aware creative synthesis, an internal filter, and adversarial research. Only then run the gates below. Run these before reference acquisition, avatar work, UI construction, or image generation.

Do not begin from MyDashPerks, a discount, a payment screen, or a desirable object. Do not invent a promise, conflict, mistake, deadline, emergency, or disagreement to turn an object into a story. A real topic is not a human event. Neighboring true facts are not a chain. A plausible purchase is not a story.

## Gate 1, organic story
Would this still be interesting if MyDashPerks disappeared? It needs a genuine human reason to keep swiping. The human event working without the perk is required. It is not a Gate 2 failure.

## Gate 2, structural fit
The campaign does not have to cause, resolve, justify, or alter the human event. Characters do not have to care about the perk. The economic loop does not have to be the same loop as the human loop.

GATE 2A, INTEGRATED ECONOMICS. The economics matter to a real decision. Shape: human problem, then a purchase decision, then economics that change whether that decision makes sense.

GATE 2B, PARALLEL ECONOMIC DISCOVERY. The human story works without the campaign. A transaction artifact that already belongs exposes a second question. The anomaly does not need to explain the human event. The iPad reference is a delivery situation plus a separate low-transaction method loop. Neither caused the other.

A candidate needs 2A or 2B, not both. Structural fit is not enough.

## Campaign salience
If campaign economics enter this transaction, do they create a new viewer question, desire, or replication impulse worth pursuing, or do they merely make an already-obvious decision cheaper?

This is not a requirement that the perk strengthen the human event. It is a requirement that the campaign contribution itself be interesting enough to carry attention.

Reject: use the free thing instead of buying another, don't pay twice, this purchase becomes slightly more rational, fees hurt less, ordinary replenishment costs less, and any takeaway whose whole point is that saving money is better.

Potentially strong: economics surprising enough that viewers audit the transaction, access to a highly desirable object changes dramatically, a visible total conflicts with normal price expectations, a method gap, economics that create replication desire, or economic evidence that is a second comment-worthy discovery.

Gate 1 pass, Gate 2 structural pass, and salience fail means preserve it as organic material and do not campaign-produce it. Do not alter the candidate to rescue salience.

Still reject: a perk name pasted onto unrelated proof, economics too ordinary to attract attention, an extra ad slide, a chronology-breaking surface, fabricated retailer behavior presented as fact, or a campaign reveal that destroys the stronger human reveal.

## Observed curiosity is not campaign space
OBSERVED RETAILER ECONOMIC CURIOSITY is only what research showed. CLEAN CAMPAIGN ECONOMIC SPACE is whether a later secondary detail would still be interpretable. Full price can be observed NONE and campaign space HIGH. An existing sale that already explains the cheapness is HIGH observed and LOW campaign space.

Research does not need to find MyDashPerks already operating. Staged campaign economics stay creative. Never report them as a verified promotion.

## Presentation modes
Use these only after the story demands a fact, a time, and a transaction state. STANDALONE UI, NESTED OR SHARED UI, or ORGANIC PHOTO PLUS SUPPORTING UI. Commerce state moves forward. Do not walk backward for a convenient perk slot.

## Synthesis
Event evidence legitimizes the human mechanic. Object evidence legitimizes the object. They do not have to come from the same source. Label researched mechanic, researched object, and original staged synthesis. Never describe the combination as a researched event. Do not copy names, dialogue, amounts, jokes, circumstances, or visual sequence.

Do not generate these plots again: overslept delivery, hidden package, food argument, dream gift, spent bill money, a dollar left, a couple misunderstanding, a shelf then a receipt, or payment as the final slide. Do not revive BYOMA as a campaign, the Cheesecake Factory vow, the modified salmon order, the migraine delivery, the diaper-gift replenishment, or the wrong-door sandwich "don't pay twice" campaign.

## Pitch
Maximum 3 pass/pass/salient candidates, or fewer. Zero is allowed. Then stop. No storyboard, no surfaces, no images.


### SKILL DEPENDENCY AUDIT
[
  {
    "dependency": "commercial-aware-synthesis",
    "reason": "dependency skill is in this stage packet",
    "skill": "synthetic-story-generator",
    "stage": "CONCEPT_GENERATION",
    "state": "included"
  },
  {
    "dependency": "story-conflict-scout",
    "reason": "stage registry did not select this dependency; structured creative state is carried separately when a StoryLock or DNA profile is in scope",
    "skill": "commercial-aware-synthesis",
    "stage": "CONCEPT_GENERATION",
    "state": "intentionally_not_included"
  },
  {
    "dependency": "object-culture-scout",
    "reason": "stage registry did not select this dependency; structured creative state is carried separately when a StoryLock or DNA profile is in scope",
    "skill": "commercial-aware-synthesis",
    "stage": "CONCEPT_GENERATION",
    "state": "intentionally_not_included"
  },
  {
    "dependency": "live-heat-scout",
    "reason": "stage registry did not select this dependency; structured creative state is carried separately when a StoryLock or DNA profile is in scope",
    "skill": "commercial-aware-synthesis",
    "stage": "CONCEPT_GENERATION",
    "state": "intentionally_not_included"
  },
  {
    "dependency": "synthetic-story-generator",
    "reason": "dependency skill is in this stage packet",
    "skill": "commercial-aware-synthesis",
    "stage": "CONCEPT_GENERATION",
    "state": "included"
  },
  {
    "dependency": "commercial-aware-synthesis",
    "reason": "dependency skill is in this stage packet",
    "skill": "adaptation-blitz-match",
    "stage": "CONCEPT_GENERATION",
    "state": "included"
  }
]

## CURRENT STORY LOCK
No current approved StoryLock is in scope.

## ACCOUNT DNA
profile 01622ddc-e913-4783-8514-ec29b6956f63 version 1 origin HUMAN_SET approval APPROVED
Included because: explicit current-approved DNA pointer
- content_lane = food and couples [HUMAN_SET_CONSTRAINT] confidence None sample None dates None..None source ACCOUNT_STATE_TODAY.md
- post_views = 338200 [HISTORICAL_OBSERVATION] confidence None sample 1 dates None..None source ACCOUNT_STATE_TODAY.md
  notes: Chick-fil-A post stated as 338.2K
- recurring_relationship = Dre as boyfriend [HUMAN_SET_CONSTRAINT] confidence None sample None dates None..None source ACCOUNT_STATE_TODAY.md

## CREATIVE GENOME
state: NONE

## BENCHMARKS
### Maria Chick-fil-A
account Maria category None ecosystem None holdout False
metrics views 338200 likes None comments None shares None saves None
lesson: source text: 338.2K
metrics note: source text: 338.2K
Included because: account match
source: BENCHMARKS.md

### Maria McChicken
account Maria category None ecosystem None holdout False
metrics views None likes None comments None shares None saves None
lesson: UNKNOWN / NEEDS FOLLOW-UP
metrics note: UNKNOWN / NEEDS FOLLOW-UP
Included because: account match
source: BENCHMARKS.md

### Brooke pink iPad / overslept
account Brooke category WINNER ecosystem None holdout False
metrics views 2300000 likes None comments None shares None saves None
lesson: source text: 2.3M
metrics note: source text: 2.3M
Included because: category WINNER
source: BENCHMARKS.md

### Brooke boyfriend pink-iPad sequel
account Brooke category WEAK ecosystem None holdout False
metrics views None likes None comments None shares None saves None
lesson: UNKNOWN
metrics note: UNKNOWN
Included because: category WEAK
source: BENCHMARKS.md

### Sarah Dasher got nosy
account Sarah category WEAK ecosystem None holdout False
metrics views None likes None comments None shares None saves None
lesson: UNKNOWN
metrics note: UNKNOWN
Included because: category WEAK
source: BENCHMARKS.md

### Cent post
account None category FAILURE ecosystem None holdout False
metrics views None likes None comments None shares None saves None
lesson: did not travel
metrics note: did not travel
Included because: category FAILURE
source: BENCHMARKS.md

### Jenny screen recording
account None category FAILURE ecosystem None holdout False
metrics views None likes None comments None shares None saves None
lesson: did not travel
metrics note: did not travel
Included because: category FAILURE
source: BENCHMARKS.md

### Lindy metadata joke
account None category FAILURE ecosystem None holdout False
metrics views None likes None comments None shares None saves None
lesson: did not travel
metrics note: did not travel
Included because: category FAILURE
source: BENCHMARKS.md

### Sarah MacBook
account Sarah category None ecosystem None holdout False
metrics views 150500 likes None comments None shares None saves None
lesson: source text: 150.5K
metrics note: source text: 150.5K
Included because: non-holdout program benchmark
source: BENCHMARKS.md

## MECHANIC HISTORY
{
  "account_id": "d7731bd4-13f7-4a1a-a68d-2dbbec49189d",
  "as_of": "2026-10-06T20:37:02.666607+00:00",
  "authority": "observation",
  "program_lifetime": [],
  "reason_included": "account-local mechanic history; no fatigue score",
  "scope": "ACCOUNT",
  "source": "mechanic_observations",
  "version": "windows",
  "windows": {
    "last_30_days": [],
    "last_7_days": [],
    "last_n_posts": [],
    "lifetime": []
  }
}

## REFERENCES AND ASSET METADATA
No visual reference metadata was selected for this stage.

## SCOPE
{
  "account": {
    "id": "d7731bd4-13f7-4a1a-a68d-2dbbec49189d",
    "name": "Maria",
    "slug": "maria"
  },
  "campaign": null,
  "creative": null,
  "ecosystem": {
    "code": "DOORDASH",
    "id": "7ef60440-4e82-49a0-85c8-07d4a323d937",
    "name": "DoorDash"
  },
  "program": {
    "id": "c0616ab6-7386-4fa3-af2c-9bac09540c4e",
    "name": "MyDashPerks",
    "slug": "mydashperks"
  }
}

## SELECTED CONCEPT
No selected concept is linked.

## COMMENT DOORS
[]

## CONTINUITY
[]

## EXCLUSIONS
[
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "find-purchase-screens-on-pinterest",
    "version_id": "c4279eea-b43c-451d-acd1-55089cb7f3f0"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "ios-26-production-normalization",
    "version_id": "45862384-e971-43c0-aeed-04ba81dff831"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "live-heat-scout",
    "version_id": "437eb9d4-8ad3-4dde-a59a-fd51c7785ee3"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "object-culture-scout",
    "version_id": "2d623443-ad89-4a0c-8701-2a5f47b4ac58"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "production-spec-qa",
    "version_id": "e5d6ae5f-a594-412c-9efe-2c7aa05d28d6"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "story-conflict-scout",
    "version_id": "ebdd8458-fe6d-433d-9e91-d4f0d45f9048"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "story-development",
    "version_id": "f7c0e0f1-b00f-429a-b7d1-af0b9e8d2c72"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage CONCEPT_GENERATION",
    "skill_role": null,
    "slug": "visual-surface-acquisition",
    "version_id": "31c11b8d-685a-4ef2-8dd2-741921672ba3"
  },
  {
    "authority": "reference example",
    "holdout": true,
    "reason_excluded": "holdout benchmark",
    "reason_included": "withheld from provider context"
  },
  {
    "authority": "reference example",
    "holdout": true,
    "reason_excluded": "holdout benchmark",
    "reason_included": "withheld from provider context"
  },
  {
    "name": "DoorDash step refs",
    "reason_excluded": "visual references are not loaded for stage CONCEPT_GENERATION",
    "version": "7ba2730c-5807-4431-9da7-4c20c5806bf3"
  },
  {
    "name": "Target reference bank V2",
    "reason_excluded": "visual references are not loaded for stage CONCEPT_GENERATION",
    "version": "076577bd-ca3a-4b28-828d-0709ee5ac382"
  }
]

SKILL COVERAGE: COVERED

## SECTION SIZES
- task: 5462 characters, token estimate 1365
- invariants: 10179 characters, token estimate 2544
- policies: 2383 characters, token estimate 595
- skills: 25250 characters, token estimate 6312
- story_lock: 64 characters, token estimate 16
- dna: 596 characters, token estimate 149
- genome: 30 characters, token estimate 7
- benchmarks: 2377 characters, token estimate 594
- mechanics: 447 characters, token estimate 111
- references: 90 characters, token estimate 22
- other: 3063 characters, token estimate 765
