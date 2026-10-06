# Creative OS provider packet
PROVIDER_EXECUTION: NOT_IMPLEMENTED
Use only this packet. Do not search the web. Do not mutate stored creative truth.
COMPILER: context-compiler-0.3.0
AS_OF: 2026-10-06T20:37:02.666607+00:00
STAGE: STORY_DEVELOPMENT

## TASK
Audit the current story as a creative director.
Determine whether the narrative is production-ready.
Preserve strong existing decisions.
Identify only meaningful remaining story-level weaknesses.
Do not redesign it simply to be different.
Do not inspect image pixels. This test is narrative and system transfer only.
Task id: b6421dc4-79e3-42b0-9652-5ae5cd64d4de
Stage: STORY_DEVELOPMENT
Status: CONSUMED
Expected output: STORY_DEVELOPMENT_AUDIT
Constraints:
{}
Input refs:
{}

## OUTPUT CONTRACT STORY_DEVELOPMENT_AUDIT
Return StoryDevelopmentAuditResult JSON only. This is a diagnosis and proposal. Do not mutate the StoryLock. Preserve decisions that are already working.
{
  "description": "Diagnosis only. The model must not mutate the StoryLock.",
  "properties": {
    "comment_door_assessment": {
      "title": "Comment Door Assessment",
      "type": "string"
    },
    "commerce_integration_assessment": {
      "title": "Commerce Integration Assessment",
      "type": "string"
    },
    "continuity_assessment": {
      "title": "Continuity Assessment",
      "type": "string"
    },
    "diagnosis": {
      "title": "Diagnosis",
      "type": "string"
    },
    "hook_assessment": {
      "title": "Hook Assessment",
      "type": "string"
    },
    "overall_status": {
      "enum": [
        "READY",
        "THIN",
        "NEEDS_CHANGES"
      ],
      "title": "Overall Status",
      "type": "string"
    },
    "proof_boundary_assessment": {
      "title": "Proof Boundary Assessment",
      "type": "string"
    },
    "propulsion_assessment": {
      "title": "Propulsion Assessment",
      "type": "string"
    },
    "recommended_changes": {
      "items": {
        "type": "string"
      },
      "title": "Recommended Changes",
      "type": "array"
    },
    "recommended_patches": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Recommended Patches",
      "type": "array"
    },
    "things_to_preserve": {
      "items": {
        "type": "string"
      },
      "title": "Things To Preserve",
      "type": "array"
    },
    "uncertainties": {
      "items": {
        "type": "string"
      },
      "title": "Uncertainties",
      "type": "array"
    },
    "viral_texture_assessment": {
      "title": "Viral Texture Assessment",
      "type": "string"
    }
  },
  "required": [
    "overall_status",
    "diagnosis",
    "hook_assessment",
    "propulsion_assessment",
    "viral_texture_assessment",
    "continuity_assessment",
    "comment_door_assessment",
    "commerce_integration_assessment",
    "proof_boundary_assessment"
  ],
  "title": "StoryDevelopmentAuditResult",
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

## CREATIVE LOCKS
### principles-d-creative-lock-note (CREATIVE LOCKED_VALUE)
version 2d1201ff-4804-4eb6-aa95-2be0adcccc5c priority authoritative authority locked_value
Included because: resolved CREATIVE LOCKED_VALUE for principles-d-creative-lock-note; retained regardless of token budget
CREATIVE-SPECIFIC LOCKS (never promote to global rules)
Target "SHE SAID IT WAS CHORE STUFF":
- Hook "my birthday is literally today 😭".
- Thread: "don't look at the order tho" / "bc you're nosy 😭" / "ok now i'm looking".
- S1 thread 4:12 with status bar 4:14. S2 status bar 4:15.
- Story date Mon Oct 5, 2026. "Order placed 8:06am Today" and "Pick up by Wed, Oct 7" at Phoenix SW.
- Items: spiral candles, Funfetti, Apple AirPods 5 at $129.99, streamers, paper towels.
- $142.97 − $125.00 + $1.26 = $19.23.
- S3: 12 candles, primary-color streamers, AirPods 5 box.
DoorDash "ONIONS NOTE WAS BLANK":
- McDonald's Double Cheeseburger with the missing "No Diced Onions" modifier.
- Overlay "he said he copied my order exactly".
Historical amounts are not global rules either: $156.05, $54.02, $8.08, $90.29.

## SKILLS
### story-development role REQUIRED
version handoff-2026-10-05 id f7c0e0f1-b00f-429a-b7d1-af0b9e8d2c72 hash f0883af775b0736c458e6c17481cf381a57074bae58c91fd9e41f85b2c0504a2
Included because: required skill for stage STORY_DEVELOPMENT
---
name: Story development
description: >-
  Use after concept lock and before final storyboard approval, production spec
  QA, or production routing. Runs three ordered passes: narrative propulsion
  (why the protagonist takes the action that reveals the proof), the
  comment-surface / micro-detail pass (viral texture), and cross-slide
  congruency (continuity ledger + state-transition test). Outputs a compact lock
  record that is the authoritative story truth. Does not pick concepts, change gates, or produce assets.
---
# Story development

## Where it sits
Concept selection / concept lock → **story development** → final storyboard approval → production spec QA / production routing.

This stage owns beat progression, viral texture, and intended cross-slide continuity. Production spec QA only verifies that these decisions survived execution; it does not originate them. This skill does not change Gate 1, Gate 2A/2B, campaign salience, Desire/Utility, commercial-aware synthesis, the promotion-first firewall, early exits, scouts, or production rules.

This stage develops a premise that already passed upstream. It does not add conflict, urgency, deadlines, characters, or desirable objects to rescue a weak premise or to make economics matter; the Adaptation Blitz and commercial-aware synthesis rules against that still apply. Stakes and details must already be consistent with the locked premise.

Run the three passes in order. Pass 2 starts only after the core story, propulsion, and proof logic are stable. Pass 3 runs after Pass 2 and before production routing.

## Pass 1 — Narrative propulsion
Applies to STORY-LED creative: judgment, misunderstanding, conflict, caught-by-proof, social event, mishap, gift, purchase consequence.

Name each narrative function:
- **HOOK** — what grabs attention?
- **STAKES** — why does this matter now? Usually one contextual fact (birthday tomorrow, party tonight, mom already asking, order just became ready). Not backstory.
- **TRIGGER** — what specific line, event, or contradiction changes the situation?
- **PROVOCATION / PRESSURE** — what makes the protagonist unable to ignore it?
- **ACTION** — what does the protagonist decide to do?
- **EXPECTED CONSEQUENCE** — what does the viewer now predict is about to happen? That prediction is part of why they swipe.
- **REVEAL** — what actually happens?

These are functions, not slides. Several can live inside one message exchange. Do not force seven beats into seven slides.

Repair the smallest missing causal beat. Preserve existing story-native setup, texture, contradictions, and useful micro-details unless they are themselves causing the propulsion failure.

Hook is not propulsion. A strange line can create attention and still motivate nothing.

### Propulsion failure test
For every proof-exposing action, ask why the protagonist does it: checks the order, opens the receipt, looks at the screenshot, replies, confronts someone, inspects the app, takes the photo, keeps scrolling.

If the answer is "because the storyboard needs the proof": **FAIL**. Repair the human causality inside the story. If a function is missing without a deliberate reason, mark the story THIN and repair before production.

### Overlay job
If S1 uses a floating TikTok hook, it adds context, stakes, or POV the artifact does not already contain. It must not restate a bubble, and it must not explain the story.

### Family D exception
Do not force interpersonal propulsion onto pure desire/method content. Family D uses: DESIRE → METHOD / ACCESS GAP → USEFUL REVEAL → PROOF / REPLICATION. The same "why would they do that?" test applies to each step.

## Pass 2 — Comment surface / micro-detail

### Viral texture
**Viral texture** = small, believable, non-essential details that reward closer inspection and create additional audience reactions without interfering with the primary story.

- A **core beat** moves the story.
- **Viral texture** makes the story richer, more inspectable, more commentable, more shareable, or more desirable.

Do not confuse them.

### Per slide
Keep ONE primary story beat. Add 0–3 secondary details only where they naturally belong. Zero is allowed. Quality over count; never add density to satisfy the rule.

Detail categories (not quotas): object, social, taste / judgment, desire, mini contradiction, realism, timing, identity, price / quantity anomaly, background callback.

### Four-question test
Every approved micro-detail must pass:
1. Would this naturally be here?
2. Does it create a new reaction, question, desire, judgment, or inspection reward?
3. Does it make the main story better?
4. Would the post still work without it?

Ideal: yes / yes / yes / yes. If removing it breaks the story, it is a CORE BEAT, not a micro-detail.

Reject details that exist only to bait comments and do not belong to the world: a random expensive product, an unrelated notification, a fake price typo, a celebrity poster.

### Discount-headroom firewall
A desirable or expensive item may NEVER be added solely to increase the subtotal, create discount headroom, make a staged savings number larger, or manufacture an economic reveal. It is allowed only when the story independently gives it a reason to exist. Example: AirPods pass as the hidden birthday gift in a sibling's order; AirPods dropped into an unrelated basket fail. This restates, and does not relax, the existing rule against padding a basket.

### Comment-door map
Before final storyboard approval, record the PRIMARY comment door and the independent SECONDARY doors. Do not require every viewer to react to the same thing. The goal is not to script comments; it is to confirm the artifacts contain several natural reaction opportunities.

## Pass 3 — Cross-slide congruency / continuity
A story-led carousel passes only if every slide belongs to the same coherent story world. Individual slides being plausible is NOT enough. The sequence must be mutually compatible across time, date, weekday, location, actor state, knowledge state, object state, order / transaction state, product identity, quantity, color / variant, economics, physical payoff, and cause and effect.

### Continuity ledger
Before the lock record becomes production-ready, record for every slide:

```
RELATIVE TIME:
VISIBLE CLOCK:
VISIBLE DATE / WEEKDAY / TODAY / YESTERDAY:
ACTOR LOCATION:
WHAT THE ACTOR KNOWS:
WHAT THE ACTOR HAS DONE:
ORDER / TRANSACTION STATE:
IMPORTANT OBJECT STATES:
LOCKED PRODUCT IDENTITIES:
LOCKED COUNTS / COLORS / VARIANTS (where relevant):
PHYSICAL PAYOFF STATE:
CAUSAL TRANSITION INTO NEXT SLIDE:
```

Keep it compact. Its job is to prevent contradictions, not create paperwork. Leave a field blank when it does not apply.

### State-transition test
For each important story element, confirm it can naturally move from slide N to slide N+1 within the implied time. Examples:
- ORDER: placed → ready → picked up → items used
- CAKE: mix ordered → acquired → baked → frosted → candles lit
- GIFT: hidden → discovered in order → acquired → physically present
- KNOWLEDGE: doesn't know → suspicious → checks → discovers → sees payoff

If a required transition is impossible or missing: **FAIL**. Fix the smallest value or state necessary (a timestamp, a date, one overlay word, a count). Do not invent extra plot to repair chronology.

### Temporal compression
Viewers perceive consecutive slides as temporally close unless the creative clearly suggests otherwise. Avoid meaningful unmarked jumps. If a jump is truly required, signal it natively; prefer adjusting the timeline so no explanation is needed. The ideal continuity is invisible: if viewers notice the timeline mechanics, it was overdone.

### Visible UI values are story facts
Any visible clock, date, weekday, Today / Yesterday, order time, pickup deadline, delivery time, arrival date, or message timestamp is part of the story world and MUST come from the continuity ledger. Do not preserve stale reference values because the base screenshot contained them. Reference Is Law governs layout, geometry, native UI appearance, spacing, cards, icons, and behavior, not story-specific clock, date, or order values.

## Current-lock precedence
The latest human-approved STORY_LOCK is the authoritative story truth. When a human-approved change supersedes an earlier value, older generated assets, prior lock versions, memory notes, drafts, and references become STALE for that field and may not override the current lock. Example: if the current lock says AirPods 5, an older S2 showing AirPods 4 is a stale asset, not competing evidence; never resurrect it.

### Stale-asset handling
When a locked field changes, list each affected prior production asset in the lock record as `STALE — REPRODUCTION REQUIRED` (or `STALE — SUPERSEDED BY CURRENT STORY_LOCK`). Do not silently keep using it, do not rewrite history, and do not delete prior files unless explicitly asked. The newest approved lock controls the next production pass.

## Output: lock record
Keep it compact. Do not expose long framework reports in normal creative review unless asked.

```
CORE STORY:
HOOK:
STAKES:
TRIGGER:
ACTION:
EXPECTED NEXT BEAT:
REVEAL / PAYOFF:
SLIDE-BY-SLIDE PRIMARY BEAT:
APPROVED MICRO-DETAILS BY SLIDE:
PRIMARY COMMENT DOOR:
SECONDARY COMMENT DOORS:
DETAILS REJECTED AS FORCED:
COMMERCE RELATION: PRIMARY / SECONDARY / INCIDENTAL
DOES STORY WORK WITHOUT ECONOMICS: YES / NO
STORY DATE:
CONTINUITY LEDGER (per slide, Pass 3 fields):
STATE-TRANSITION CHECK: PASS / FAIL (+ any fix)
STALE ASSETS (superseded fields):
READY FOR PRODUCTION: YES / NO
```

Save the lock record beside the concept's outputs (for example `STORY_LOCK.md`). Production spec QA reads it; production may not add, drop, or swap approved details or continuity values without returning here.


### SKILL DEPENDENCY AUDIT
[
  {
    "dependency": "adaptation-blitz-match",
    "reason": "stage registry did not select this dependency; structured creative state is carried separately when a StoryLock or DNA profile is in scope",
    "skill": "story-development",
    "stage": "STORY_DEVELOPMENT",
    "state": "intentionally_not_included"
  }
]

## CURRENT STORY LOCK
version 1 id 08c56ceb-91a9-4ab3-b853-58faa458b933 document_hash 7899292fc644604e9c61802d6fc9fe714826465497b4a3db9398e85c8b357844
# STORY LOCK — SHE SAID IT WAS CHORE STUFF (Target) — story-development record, 2026-10-05
CURRENT LOCK REVISION: continuity update, 2026-10-05 ~9:10 PM ET (Tyrel-approved). This file is the authoritative story truth; older assets, drafts, memory notes and references are STALE for any field changed here.
LABEL: FICTIONAL / STAGED. Economics are staged creative values, NOT a verified Target promotion or program.

CORE STORY: Sister says she's grabbing house stuff and tells narrator not to look at the order; narrator looks; it's their birthday surprise (party supplies + AirPods), and the order total is oddly low.
HOOK: "don't look at the order tho"
STAKES: narrator's birthday is TODAY (floating hook only)
TRIGGER / PROVOCATION: narrator resists ("why would i look"); sister provokes ("bc you're nosy 😭")
ACTION: narrator opens the order
EXPECTED NEXT BEAT: "she's hiding something for my birthday — what's in it?"
REVEAL / PAYOFF: S2 order = birthday stuff + paper towels cover + AirPods, total $19.23; S3 birthday surprise photo

S1 DIALOGUE — LOCKED (Tyrel, 2026-10-05):
  sis (incoming): grabbing stuff for the house rn
  sis (incoming): don't look at the order tho
  me (outgoing): why would i look
  sis (incoming): bc you're nosy 😭
  me (outgoing): ok now i'm looking
S1 FLOATING HOOK — LOCKED: "my birthday is literally today 😭"   (superseded: "my birthday is literally tomorrow 😭")
Rejected: option A ("it literally just popped up on my phone" / "DON'T open it" / "well now i'm opening it") — constructed, dropped the "stuff for the house" setup.
S1 base: /workspace/creative-pipeline/shared/templates/ios-messages-keyboard/keyboard_thread_base_ios26_dark.png
S1 withholds: Target, Drive Up, birthday supplies, AirPods, discount, MyDashPerks.

SLIDE-BY-SLIDE PRIMARY BEAT:
  S1 — sister forbids looking; narrator decides to look
  S2 — the order (Target Order Details, Ready for pickup)
  S3 — birthday surprise camera-roll photo

APPROVED MICRO-DETAILS BY SLIDE:
  S1 — contact "sis" (social); "bc you're nosy 😭" sibling-coded provocation (social); "stuff for the house" cover (sets up paper-towel callback)
  S2 — gold/silver tall spiral candles (desire); AirPods 5 mid-list, same thumbnail size (desire / mini contradiction); paper towels LAST (mini contradiction / cover story); $19.23 total (price anomaly)
  S3 — gold/silver spiral candles on the cake (continuity/desire); white AirPods box opened or half-unwrapped near the frame edge, partly cropped, not centered (background callback); optional paper towel roll in background (callback); crooked streamers (realism)

S2 LOCKED ITEMS (top → bottom):
  1. Gold/Silver Tall Spiral Birthday Candles 12ct - Spritz™ (TCIN 92290028) — $3.00
  2. Pillsbury Funfetti Premium Cake & Cupcake Mix - 15.25oz — $1.99
  3. Apple AirPods 5 Wireless Earbuds — $129.99   (Tyrel-locked 2026-10-05; superseded: Apple AirPods 4 Wireless Earbuds, TCIN 85978615)
  4. 4pk Primary Color Rainbow Crepe Streamer - Spritz™ — $3.00
  5. Bounty Select-A-Size Paper Towels - 1 Mega Roll — $4.99
  Prices: candles/Funfetti/streamers/Bounty from cached Target snippets, not confirmed live on 10/5 (Target bot-check). AirPods 5 at $129.99 is the human-approved current product and price.

S2 LOCKED MATH (staged):
  Subtotal                  $142.97
  mydashperks.com Discount  -$125.00
  Tax                         $1.26
  Total                      $19.23
  142.97 − 125.00 = 17.97; 17.97 × 7% = 1.2579 → 1.26; 17.97 + 1.26 = 19.23
  Do not increase the discount for shock. Discount does not appear in S1 dialogue, hook, character reaction, or a separate savings slide.

PRIMARY COMMENT DOOR: why did she say not to look?
SECONDARY COMMENT DOORS: THE AIRPODS?? / she said house stuff and bought AirPods 😭 / those candles are cute / the paper towels as cover / I would've checked too / your sister is sweet / wait how was all of that only $19?

DETAILS REJECTED AS FORCED: lone gold "1" candle (competing joke); AirPods Pro 3 (parent-gift price, reads less natural); relighting trick candles (not sold at Target); Target sale price $99.99 (would explain the low total).
COMMERCE RELATION: SECONDARY
DOES STORY WORK WITHOUT ECONOMICS: YES

Image refs: /workspace/creative-pipeline/shared/research/target-airpods-candles-20261005/

STORY DATE: Monday, Oct 5, 2026

CONTINUITY LEDGER
S1
  RELATIVE TIME: afternoon, birthday day
  VISIBLE CLOCK: thread "Today 4:12 PM"; status bar 4:14
  OVERLAY: my birthday is literally today 😭
  ACTOR LOCATION: narrator at home, ordinary phone context
  KNOWS: sis says she's grabbing house stuff; does NOT know what's in the order
  HAS DONE: called nosy → decides to check ("ok now i'm looking")
  ORDER STATE: placed earlier (8:06 AM), not yet seen by narrator
  TRANSITION: narrator opens the Target order immediately
S2
  VISIBLE CLOCK: status bar 4:15 (tiny nearby variation only if the approved base forces it)
  VISIBLE DATE: "Order placed 8:06am Today"; "Pick up by Wed, Oct 7" (Oct 7, 2026 = Wednesday ✔)
  STATUS: Ready for pickup (Drive Up at Phoenix SW)
  ACTOR LOCATION: narrator viewing the order; sis about to collect it at Phoenix SW
  KNOWS (now discovers): birthday supplies, AirPods 5, paper towels, low total
  ORDER STATE: ready for pickup, not yet picked up
  LOCKED PRODUCTS: candles 12ct gold/silver spiral; Funfetti mix; Apple AirPods 5 Wireless Earbuds $129.99; 4pk primary-color rainbow crepe streamers; Bounty Mega Roll (last)
  ECONOMICS (unchanged): Subtotal $142.97 / mydashperks.com Discount -$125.00 / Tax $1.26 / Total $19.23
  TRANSITION: sis picks up → supplies used → gift physically present → celebration later that evening
S3
  RELATIVE TIME: later the same evening; no visible clock required
  ACTOR LOCATION: home kitchen
  ORDER STATE: picked up and used
  CAKE: baked, frosted (Funfetti-style), candles lit
  CANDLES: contents of one 12ct gold/silver spiral pack; prefer exactly 12 visible lit; never 14+
  STREAMERS: match the ordered primary-color rainbow crepe streamers; no pastel/ombre style
  GIFT: AirPods 5 physically present, packaging from a real AirPods 5 reference; opened, half-unwrapped, or sitting near the edge; never the hero
  PAPER TOWEL: optional subtle background callback
  KNOWS: narrator understands the surprise
  PAYOFF: birthday happened; the suspicious order was birthday prep + gift
  GIFT-OPENING ORDER: an opened gift before cake is plausible; change the box state only if the final composition reads as confusing (not a defect)

STATE-TRANSITION CHECK: PASS on this ledger
  ORDER placed 8:06 AM → ready (seen 4:15 PM) → picked up → used that evening
  CAKE mix ordered → acquired at pickup → baked/frosted → candles lit (same evening)
  GIFT hidden → discovered in order → acquired → present at birthday
  KNOWLEDGE unaware → suspicious → checks → discovers → sees payoff

STALE ASSETS (do not use; not deleted):
  v5/s2_attempt1.png — STALE — SUPERSEDED BY CURRENT STORY_LOCK (AirPods 4 row; status bar 4:31; "Pick up by Wed, Oct 23")
  v5/s1_attempt2.png — STALE — REPRODUCTION REQUIRED (hook says "tomorrow")
  v5/s1_attempt1.png, v4/s1_attempt1.png, v4/s1_attempt2.png, v4/s1_kb_attempt1.png — STALE — REPRODUCTION REQUIRED (hook says "tomorrow" / earlier attempts)
  v5/s3_attempt1.png — STALE — REPRODUCTION REQUIRED (~14 candles vs one 12ct pack; pastel/ombre streamers; AirPods packaging not matched to AirPods 5)

NEXT REPRODUCTION PASS MUST CORRECT:
  S1: hook tomorrow → today
  S2: status bar ≈4:15; Pick up by Wed, Oct 7; AirPods 5 row (Tyrel's corrected screenshot may serve as the AirPods 5 reference)
  S3: AirPods 5 packaging continuity; ~12 spiral candles; primary-color streamer continuity

READY FOR PRODUCTION: YES — current lock above; reproduce on authorization.

CURRENT PRODUCTION FILES (v5 folder): s1_v6b.png, s2_v6.png, s3_v6.png


### STORY LOCK DOCUMENT
{
  "action": "narrator opens the order",
  "comment_doors": [
    {
      "kind": "primary",
      "text": "why did she say not to look?"
    },
    {
      "kind": "secondary",
      "text": "THE AIRPODS??"
    },
    {
      "kind": "secondary",
      "text": "she said house stuff and bought AirPods 😭"
    },
    {
      "kind": "secondary",
      "text": "those candles are cute"
    },
    {
      "kind": "secondary",
      "text": "the paper towels as cover"
    },
    {
      "kind": "secondary",
      "text": "I would've checked too"
    },
    {
      "kind": "secondary",
      "text": "your sister is sweet"
    },
    {
      "kind": "secondary",
      "text": "wait how was all of that only $19?"
    }
  ],
  "commerce_relation": "SECONDARY",
  "continuity": [
    {
      "field": "RELATIVE TIME",
      "slide_index": 1,
      "value": "afternoon, birthday day"
    },
    {
      "field": "VISIBLE CLOCK",
      "slide_index": 1,
      "value": "thread \"Today 4:12 PM\"; status bar 4:14"
    },
    {
      "field": "OVERLAY",
      "slide_index": 1,
      "value": "my birthday is literally today 😭"
    },
    {
      "field": "ACTOR LOCATION",
      "slide_index": 1,
      "value": "narrator at home, ordinary phone context"
    },
    {
      "field": "KNOWS",
      "slide_index": 1,
      "value": "sis says she's grabbing house stuff; does NOT know what's in the order"
    },
    {
      "field": "HAS DONE",
      "slide_index": 1,
      "value": "called nosy → decides to check (\"ok now i'm looking\")"
    },
    {
      "field": "ORDER STATE",
      "slide_index": 1,
      "value": "placed earlier (8:06 AM), not yet seen by narrator"
    },
    {
      "field": "TRANSITION",
      "slide_index": 1,
      "value": "narrator opens the Target order immediately"
    },
    {
      "field": "VISIBLE CLOCK",
      "slide_index": 2,
      "value": "status bar 4:15 (tiny nearby variation only if the approved base forces it)"
    },
    {
      "field": "VISIBLE DATE",
      "slide_index": 2,
      "value": "\"Order placed 8:06am Today\"; \"Pick up by Wed, Oct 7\" (Oct 7, 2026 = Wednesday ✔)"
    },
    {
      "field": "STATUS",
      "slide_index": 2,
      "value": "Ready for pickup (Drive Up at Phoenix SW)"
    },
    {
      "field": "ACTOR LOCATION",
      "slide_index": 2,
      "value": "narrator viewing the order; sis about to collect it at Phoenix SW"
    },
    {
      "field": "KNOWS (now discovers)",
      "slide_index": 2,
      "value": "birthday supplies, AirPods 5, paper towels, low total"
    },
    {
      "field": "ORDER STATE",
      "slide_index": 2,
      "value": "ready for pickup, not yet picked up"
    },
    {
      "field": "LOCKED PRODUCTS",
      "slide_index": 2,
      "value": "candles 12ct gold/silver spiral; Funfetti mix; Apple AirPods 5 Wireless Earbuds $129.99; 4pk primary-color rainbow crepe streamers; Bounty Mega Roll (last)"
    },
    {
      "field": "ECONOMICS (unchanged)",
      "slide_index": 2,
      "value": "Subtotal $142.97 / mydashperks.com Discount -$125.00 / Tax $1.26 / Total $19.23"
    },
    {
      "field": "TRANSITION",
      "slide_index": 2,
      "value": "sis picks up → supplies used → gift physically present → celebration later that evening"
    },
    {
      "field": "RELATIVE TIME",
      "slide_index": 3,
      "value": "later the same evening; no visible clock required"
    },
    {
      "field": "ACTOR LOCATION",
      "slide_index": 3,
      "value": "home kitchen"
    },
    {
      "field": "ORDER STATE",
      "slide_index": 3,
      "value": "picked up and used"
    },
    {
      "field": "CAKE",
      "slide_index": 3,
      "value": "baked, frosted (Funfetti-style), candles lit"
    },
    {
      "field": "CANDLES",
      "slide_index": 3,
      "value": "contents of one 12ct gold/silver spiral pack; prefer exactly 12 visible lit; never 14+"
    },
    {
      "field": "STREAMERS",
      "slide_index": 3,
      "value": "match the ordered primary-color rainbow crepe streamers; no pastel/ombre style"
    },
    {
      "field": "GIFT",
      "slide_index": 3,
      "value": "AirPods 5 physically present, packaging from a real AirPods 5 reference; opened, half-unwrapped, or sitting near the edge; never the hero"
    },
    {
      "field": "PAPER TOWEL",
      "slide_index": 3,
      "value": "optional subtle background callback"
    },
    {
      "field": "KNOWS",
      "slide_index": 3,
      "value": "narrator understands the surprise"
    },
    {
      "field": "PAYOFF",
      "slide_index": 3,
      "value": "birthday happened; the suspicious order was birthday prep + gift"
    },
    {
      "field": "GIFT-OPENING ORDER",
      "slide_index": 3,
      "value": "an opened gift before cake is plausible; change the box state only if the final composition reads as confusing (not a defect)"
    }
  ],
  "core_story": "Sister says she's grabbing house stuff and tells narrator not to look at the order; narrator looks; it's their birthday surprise (party supplies + AirPods), and the order total is oddly low.",
  "dialogue": [
    {
      "direction": "incoming",
      "speaker": "sis",
      "text": "grabbing stuff for the house rn"
    },
    {
      "direction": "incoming",
      "speaker": "sis",
      "text": "don't look at the order tho"
    },
    {
      "direction": "outgoing",
      "speaker": "me",
      "text": "why would i look"
    },
    {
      "direction": "incoming",
      "speaker": "sis",
      "text": "bc you're nosy 😭"
    },
    {
      "direction": "outgoing",
      "speaker": "me",
      "text": "ok now i'm looking"
    }
  ],
  "economics": {
    "discount": "125.00",
    "discount_label": "mydashperks.com Discount",
    "notes": "Parsed from the story lock economics block. Staged when the lock says so.",
    "staged": true,
    "subtotal": "142.97",
    "tax": "1.26",
    "total": "19.23"
  },
  "expected_next_beat": "\"she's hiding something for my birthday — what's in it?\"",
  "extra": {},
  "floating_hook": "my birthday is literally today 😭",
  "hook": "don't look at the order tho",
  "label": "FICTIONAL / STAGED. Economics are staged creative values, NOT a verified Target promotion or program.",
  "line_items": [
    {
      "color": null,
      "external_id": "92290028",
      "generation": null,
      "model": null,
      "pack_count": 12,
      "position": 1,
      "quantity": null,
      "title": "Gold/Silver Tall Spiral Birthday Candles 12ct - Spritz™",
      "unit_price": "3.00",
      "variant": null
    },
    {
      "color": null,
      "external_id": null,
      "generation": null,
      "model": null,
      "pack_count": null,
      "position": 2,
      "quantity": null,
      "title": "Pillsbury Funfetti Premium Cake & Cupcake Mix - 15.25oz",
      "unit_price": "1.99",
      "variant": null
    },
    {
      "color": null,
      "external_id": "85978615",
      "generation": "5",
      "model": "AirPods 5",
      "pack_count": null,
      "position": 3,
      "quantity": null,
      "title": "Apple AirPods 5 Wireless Earbuds",
      "unit_price": "129.99",
      "variant": null
    },
    {
      "color": null,
      "external_id": null,
      "generation": null,
      "model": null,
      "pack_count": null,
      "position": 4,
      "quantity": null,
      "title": "4pk Primary Color Rainbow Crepe Streamer - Spritz™",
      "unit_price": "3.00",
      "variant": null
    },
    {
      "color": null,
      "external_id": null,
      "generation": null,
      "model": null,
      "pack_count": null,
      "position": 5,
      "quantity": null,
      "title": "Bounty Select-A-Size Paper Towels - 1 Mega Roll",
      "unit_price": "4.99",
      "variant": null
    }
  ],
  "reveal": "S2 order = birthday stuff + paper towels cover + AirPods, total $19.23; S3 birthday surprise photo",
  "slides": [
    {
      "actor_knowledge": "sis says she's grabbing house stuff; does NOT know what's in the order",
      "actor_location": "narrator at home, ordinary phone context",
      "beat": "sister forbids looking; narrator decides to look",
      "index": 1,
      "order_state": "placed earlier (8:06 AM), not yet seen by narrator",
      "overlay": "my birthday is literally today 😭",
      "relative_time": "afternoon, birthday day",
      "visible_clock": "4:14 PM",
      "visible_date": null
    },
    {
      "actor_knowledge": "birthday supplies, AirPods 5, paper towels, low total",
      "actor_location": "narrator viewing the order; sis about to collect it at Phoenix SW",
      "beat": "the order (Target Order Details, Ready for pickup)",
      "index": 2,
      "order_state": "ready for pickup, not yet picked up",
      "overlay": null,
      "relative_time": null,
      "visible_clock": "status bar 4:15",
      "visible_date": "\"Order placed 8:06am Today\"; \"Pick up by Wed, Oct 7\" (Oct 7, 2026 = Wednesday ✔)"
    },
    {
      "actor_knowledge": "narrator understands the surprise",
      "actor_location": "home kitchen",
      "beat": "birthday surprise camera-roll photo",
      "index": 3,
      "order_state": "picked up and used",
      "overlay": null,
      "relative_time": "later the same evening; no visible clock required",
      "visible_clock": null,
      "visible_date": null
    }
  ],
  "stakes": "narrator's birthday is TODAY (floating hook only)",
  "stale_notes": [
    "v5/s2_attempt1.png — STALE — SUPERSEDED BY CURRENT STORY_LOCK (AirPods 4 row; status bar 4:31; \"Pick up by Wed, Oct 23\")",
    "v5/s1_attempt2.png — STALE — REPRODUCTION REQUIRED (hook says \"tomorrow\")",
    "v5/s1_attempt1.png, v4/s1_attempt1.png, v4/s1_attempt2.png, v4/s1_kb_attempt1.png — STALE — REPRODUCTION REQUIRED (hook says \"tomorrow\" / earlier attempts)",
    "v5/s3_attempt1.png — STALE — REPRODUCTION REQUIRED (~14 candles vs one 12ct pack; pastel/ombre streamers; AirPods packaging not matched to AirPods 5)"
  ],
  "story_date": "2026-10-05",
  "story_weekday": "Monday",
  "story_works_without_economics": true,
  "title": "SHE SAID IT WAS CHORE STUFF (Target) — story-development record, 2026-10-05",
  "trigger": "narrator resists (\"why would i look\"); sister provokes (\"bc you're nosy 😭\")",
  "viral_texture": [
    {
      "category": null,
      "slide_index": 1,
      "text": "contact \"sis\" (social); \"bc you're nosy 😭\" sibling-coded provocation (social); \"stuff for the house\" cover (sets up paper-towel callback)"
    },
    {
      "category": null,
      "slide_index": 2,
      "text": "gold/silver tall spiral candles (desire); AirPods 5 mid-list, same thumbnail size (desire / mini contradiction); paper towels LAST (mini contradiction / cover story); $19.23 total (price anomaly)"
    },
    {
      "category": null,
      "slide_index": 3,
      "text": "gold/silver spiral candles on the cake (continuity/desire); white AirPods box opened or half-unwrapped near the frame edge, partly cropped, not centered (background callback); optional paper towel roll in background (callback); crooked streamers (realism)"
    }
  ]
}

## ACCOUNT DNA
No approved Account DNA profile is in scope.

## CREATIVE GENOME
state: BOUND
id d6a1e39b-dcc3-4c0f-aaac-ccce3c1bcd8d version import-2026-10-05 origin HUMAN_SET approval APPROVED story_lock 08c56ceb-91a9-4ab3-b853-58faa458b933
- commerce_integration = SECONDARY assignment human_set confidence None source story lock COMMERCE RELATION
- ecosystem = TARGET assignment human_set confidence None source story lock title names Target
- floating_hook = my birthday is literally today 😭 assignment human_set confidence None source story lock floating hook
- hook_text = don't look at the order tho assignment human_set confidence None source story lock HOOK
- label = FICTIONAL / STAGED. Economics are staged creative values, NOT a verified Target promotion or program. assignment human_set confidence None source story lock LABEL
- slide_count = 3 assignment human_set confidence None source continuity ledger headings
- story_works_without_economics = yes assignment human_set confidence None source story lock DOES STORY WORK WITHOUT ECONOMICS

## BENCHMARKS
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

### Maria Chick-fil-A
account Maria category None ecosystem None holdout False
metrics views 338200 likes None comments None shares None saves None
lesson: source text: 338.2K
metrics note: source text: 338.2K
Included because: non-holdout program benchmark
source: BENCHMARKS.md

### Maria McChicken
account Maria category None ecosystem None holdout False
metrics views None likes None comments None shares None saves None
lesson: UNKNOWN / NEEDS FOLLOW-UP
metrics note: UNKNOWN / NEEDS FOLLOW-UP
Included because: non-holdout program benchmark
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
  "account_id": null,
  "as_of": "2026-10-06T20:37:02.666607+00:00",
  "authority": "observation",
  "program_lifetime": [
    {
      "count": 1,
      "dimension": "commerce_integration",
      "value": "SECONDARY"
    },
    {
      "count": 1,
      "dimension": "ecosystem",
      "value": "TARGET"
    },
    {
      "count": 1,
      "dimension": "hook_pattern",
      "value": "my birthday is literally today 😭"
    },
    {
      "count": 1,
      "dimension": "proof_surface",
      "value": "order_details"
    }
  ],
  "reason_included": "account-local mechanic history; no fatigue score",
  "scope": "UNSCOPED",
  "source": "mechanic_observations",
  "version": "windows",
  "windows": {
    "last_30_days": [
      {
        "count": 1,
        "dimension": "commerce_integration",
        "value": "SECONDARY"
      },
      {
        "count": 1,
        "dimension": "ecosystem",
        "value": "TARGET"
      },
      {
        "count": 1,
        "dimension": "hook_pattern",
        "value": "my birthday is literally today 😭"
      },
      {
        "count": 1,
        "dimension": "proof_surface",
        "value": "order_details"
      }
    ],
    "last_7_days": [
      {
        "count": 1,
        "dimension": "commerce_integration",
        "value": "SECONDARY"
      },
      {
        "count": 1,
        "dimension": "ecosystem",
        "value": "TARGET"
      },
      {
        "count": 1,
        "dimension": "hook_pattern",
        "value": "my birthday is literally today 😭"
      },
      {
        "count": 1,
        "dimension": "proof_surface",
        "value": "order_details"
      }
    ],
    "last_n_posts": [],
    "lifetime": [
      {
        "count": 1,
        "dimension": "commerce_integration",
        "value": "SECONDARY"
      },
      {
        "count": 1,
        "dimension": "ecosystem",
        "value": "TARGET"
      },
      {
        "count": 1,
        "dimension": "hook_pattern",
        "value": "my birthday is literally today 😭"
      },
      {
        "count": 1,
        "dimension": "proof_surface",
        "value": "order_details"
      }
    ]
  }
}

## REFERENCES AND ASSET METADATA
No visual reference metadata was selected for this stage.

## SCOPE
{
  "account": null,
  "campaign": {
    "id": "0d6c6304-057e-4a8f-a6e7-b510cfe24144",
    "name": "October 2026 benchmarks",
    "slug": "october-2026-benchmarks"
  },
  "creative": {
    "holdout": true,
    "id": "b0840313-1060-4967-bfb4-fe0a3350ef3b",
    "name": "SHE SAID IT WAS CHORE STUFF",
    "slug": "chore-stuff-target",
    "status": "produced"
  },
  "ecosystem": {
    "code": "TARGET",
    "id": "896685eb-397f-4ea4-9a2f-72166a9fec8f",
    "name": "Target"
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
[
  {
    "authority": "approved story lock",
    "kind": "primary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "why did she say not to look?",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  },
  {
    "authority": "approved story lock",
    "kind": "secondary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "THE AIRPODS??",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  },
  {
    "authority": "approved story lock",
    "kind": "secondary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "she said house stuff and bought AirPods 😭",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  },
  {
    "authority": "approved story lock",
    "kind": "secondary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "those candles are cute",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  },
  {
    "authority": "approved story lock",
    "kind": "secondary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "the paper towels as cover",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  },
  {
    "authority": "approved story lock",
    "kind": "secondary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "I would've checked too",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  },
  {
    "authority": "approved story lock",
    "kind": "secondary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "your sister is sweet",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  },
  {
    "authority": "approved story lock",
    "kind": "secondary",
    "reason_included": "comment door stored on the current story lock",
    "scope": "CREATIVE",
    "source": "story lock document",
    "text": "wait how was all of that only $19?",
    "version": "08c56ceb-91a9-4ab3-b853-58faa458b933"
  }
]

## CONTINUITY
[
  {
    "field": "RELATIVE TIME",
    "slide_index": 1,
    "value": "afternoon, birthday day"
  },
  {
    "field": "VISIBLE CLOCK",
    "slide_index": 1,
    "value": "thread \"Today 4:12 PM\"; status bar 4:14"
  },
  {
    "field": "OVERLAY",
    "slide_index": 1,
    "value": "my birthday is literally today 😭"
  },
  {
    "field": "ACTOR LOCATION",
    "slide_index": 1,
    "value": "narrator at home, ordinary phone context"
  },
  {
    "field": "KNOWS",
    "slide_index": 1,
    "value": "sis says she's grabbing house stuff; does NOT know what's in the order"
  },
  {
    "field": "HAS DONE",
    "slide_index": 1,
    "value": "called nosy → decides to check (\"ok now i'm looking\")"
  },
  {
    "field": "ORDER STATE",
    "slide_index": 1,
    "value": "placed earlier (8:06 AM), not yet seen by narrator"
  },
  {
    "field": "TRANSITION",
    "slide_index": 1,
    "value": "narrator opens the Target order immediately"
  },
  {
    "field": "VISIBLE CLOCK",
    "slide_index": 2,
    "value": "status bar 4:15 (tiny nearby variation only if the approved base forces it)"
  },
  {
    "field": "VISIBLE DATE",
    "slide_index": 2,
    "value": "\"Order placed 8:06am Today\"; \"Pick up by Wed, Oct 7\" (Oct 7, 2026 = Wednesday ✔)"
  },
  {
    "field": "STATUS",
    "slide_index": 2,
    "value": "Ready for pickup (Drive Up at Phoenix SW)"
  },
  {
    "field": "ACTOR LOCATION",
    "slide_index": 2,
    "value": "narrator viewing the order; sis about to collect it at Phoenix SW"
  },
  {
    "field": "KNOWS (now discovers)",
    "slide_index": 2,
    "value": "birthday supplies, AirPods 5, paper towels, low total"
  },
  {
    "field": "ORDER STATE",
    "slide_index": 2,
    "value": "ready for pickup, not yet picked up"
  },
  {
    "field": "LOCKED PRODUCTS",
    "slide_index": 2,
    "value": "candles 12ct gold/silver spiral; Funfetti mix; Apple AirPods 5 Wireless Earbuds $129.99; 4pk primary-color rainbow crepe streamers; Bounty Mega Roll (last)"
  },
  {
    "field": "ECONOMICS (unchanged)",
    "slide_index": 2,
    "value": "Subtotal $142.97 / mydashperks.com Discount -$125.00 / Tax $1.26 / Total $19.23"
  },
  {
    "field": "TRANSITION",
    "slide_index": 2,
    "value": "sis picks up → supplies used → gift physically present → celebration later that evening"
  },
  {
    "field": "RELATIVE TIME",
    "slide_index": 3,
    "value": "later the same evening; no visible clock required"
  },
  {
    "field": "ACTOR LOCATION",
    "slide_index": 3,
    "value": "home kitchen"
  },
  {
    "field": "ORDER STATE",
    "slide_index": 3,
    "value": "picked up and used"
  },
  {
    "field": "CAKE",
    "slide_index": 3,
    "value": "baked, frosted (Funfetti-style), candles lit"
  },
  {
    "field": "CANDLES",
    "slide_index": 3,
    "value": "contents of one 12ct gold/silver spiral pack; prefer exactly 12 visible lit; never 14+"
  },
  {
    "field": "STREAMERS",
    "slide_index": 3,
    "value": "match the ordered primary-color rainbow crepe streamers; no pastel/ombre style"
  },
  {
    "field": "GIFT",
    "slide_index": 3,
    "value": "AirPods 5 physically present, packaging from a real AirPods 5 reference; opened, half-unwrapped, or sitting near the edge; never the hero"
  },
  {
    "field": "PAPER TOWEL",
    "slide_index": 3,
    "value": "optional subtle background callback"
  },
  {
    "field": "KNOWS",
    "slide_index": 3,
    "value": "narrator understands the surprise"
  },
  {
    "field": "PAYOFF",
    "slide_index": 3,
    "value": "birthday happened; the suspicious order was birthday prep + gift"
  },
  {
    "field": "GIFT-OPENING ORDER",
    "slide_index": 3,
    "value": "an opened gift before cake is plausible; change the box state only if the final composition reads as confusing (not a defect)"
  }
]

## EXCLUSIONS
[
  {
    "authority": "stage registry",
    "reason_excluded": "optional specialist not requested for this task",
    "skill_role": "OPTIONAL_SPECIALIST",
    "slug": "chat-story-slideshow"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "adaptation-blitz-match",
    "version_id": "f0a2e950-377a-4db5-b71d-8dbec361cfa9"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "commercial-aware-synthesis",
    "version_id": "95b07559-0be2-4a37-9fbe-88d0ab9eb575"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "find-purchase-screens-on-pinterest",
    "version_id": "c4279eea-b43c-451d-acd1-55089cb7f3f0"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "ios-26-production-normalization",
    "version_id": "45862384-e971-43c0-aeed-04ba81dff831"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "live-heat-scout",
    "version_id": "437eb9d4-8ad3-4dde-a59a-fd51c7785ee3"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "object-culture-scout",
    "version_id": "2d623443-ad89-4a0c-8701-2a5f47b4ac58"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "production-spec-qa",
    "version_id": "e5d6ae5f-a594-412c-9efe-2c7aa05d28d6"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "story-conflict-scout",
    "version_id": "ebdd8458-fe6d-433d-9e91-d4f0d45f9048"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
    "skill_role": null,
    "slug": "synthetic-story-generator",
    "version_id": "5e5b7693-4b34-4aca-9902-2dc6bf7b98ed"
  },
  {
    "authority": "stage registry",
    "reason_excluded": "not part of stage STORY_DEVELOPMENT",
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
    "reason_excluded": "visual references are not loaded for stage STORY_DEVELOPMENT",
    "version": "7ba2730c-5807-4431-9da7-4c20c5806bf3"
  },
  {
    "name": "Target reference bank V2",
    "reason_excluded": "visual references are not loaded for stage STORY_DEVELOPMENT",
    "version": "076577bd-ca3a-4b28-828d-0709ee5ac382"
  }
]

SKILL COVERAGE: COVERED

## SECTION SIZES
- task: 2712 characters, token estimate 678
- invariants: 10179 characters, token estimate 2544
- policies: 3481 characters, token estimate 870
- skills: 10395 characters, token estimate 2598
- story_lock: 19044 characters, token estimate 4761
- dna: 59 characters, token estimate 14
- genome: 994 characters, token estimate 248
- benchmarks: 2409 characters, token estimate 602
- mechanics: 2156 characters, token estimate 539
- references: 90 characters, token estimate 22
- other: 10149 characters, token estimate 2537
