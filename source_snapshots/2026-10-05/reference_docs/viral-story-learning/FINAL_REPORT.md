# FINAL REPORT: MyDashPerks viral-story learning + synthetic story generator

Executor subagent, Mon 2026-10-05. Work ran 2:14–2:26 PM ET by box clock. All paths are relative to `/workspace/creative-pipeline/shared/research/viral-story-learning/` unless absolute.

The exact §1–36 headings from the user's brief were not passed to this executor, so the 36 sections below map one-to-one onto the requested deliverables.

## §1 One-line status
Inventory, analysis and generator design are complete. The skill is drafted but **NOT installed**: UpdateSkill is not available to the executor. The A–F generation test and the blind contrast test both ran. Protected skills are untouched (hash MATCH).

## §2 Core correction applied
- Stories may be fictional/staged. P01 and P02 were staged and won.
- The corpus is used to learn mechanics, psychology, surface grammar and winner/loser contrast.
- RESEARCH mode never invents facts. CREATIVE mode invents characters and situations, labeled FICTIONAL/STAGED.
- Mechanic transfer: yes. Plot copying: no.
- The SER co-location direction is STOPPED. Its comment analysis was reused only as data.

## §3 Protected skills: freeze
- **When and how:** START hashes taken 2:14:23 PM ET of all 14 files under `/home/box/agent-data/workflows/`. Saved in `_hashes_start.txt`.
- **What was never written:**
  - commercial-aware-synthesis
  - V1.1/V1.2, NO TRANSITION
  - Gate 1/2A/2B
  - Campaign Salience, Desire/Utility
  - Live Heat, Object & Culture, Story & Conflict
  - Production QA, Adaptation Blitz
- **Read-only access:** commercial-aware-synthesis SKILL.md was read only to place the generator correctly.

## §4 Inventory method
- **Broad search before any claim of "need more":** `rg` and `find` across the creative-pipeline tree, agent attachments/assets and uploads.
- **Image index:** 745 unique images, deduped by content hash, in `_w/attach_index.json`. Contact sheets are in `_w/sheets/`.

## §5 Locations searched
- `/workspace/creative-pipeline/`:
  - `outputs/`
  - `shared/context/`
  - `shared/research/` (hooks-tutpinned ×2, lane-b-fyp-probe, ser-diagnostic, benchmark-run6, prior runs)
  - `sources/cards/`
  - `HANDOFF_ASSETS/`, `_examples_stage/`, `assets/`
  - `SYSTEM_PLAYBOOK.md`, `HANDOFF_LATEST.md`, `CATCHUP.md`
- `/home/box/agent-data/`: `agents/*/attachments`, `agents/*/assets`, `workflows/` (read-only), `managed-skills/skill-authoring`.
- `/workspace/uploads`.

## §6 Visual inspection
These were opened with Read and inspected (not text-only):
- **P01:** all 3 slides.
- **P02:** 2 slides plus the early comment screenshot.
- **P03 / GE-005:** 3 slides.
- **P06:** chats, receipt and the 3 porch variants.
- **P07:** the order slide.
- **P08:** 2 slides.
- **P09:** slide 1.
- **P11 and P12:** the cent builds.
- **References:** GE-001…008, R08–R17.
- **External:** FYP keyframes and tut-pinned covers/review sheets.
- **Contact sheets** of the full 745-image index.

Analyzed for each: slide order, surface change, native UI vs overlay text, withhold/reveal, proof feel, phone-native vs ad-like (see the cards).

## §7 Corpus counts
**161 usable creative examples:**

| Bucket | Count |
|---|---|
| Own posted | 11 |
| Own posting-unknown | 1 |
| Own unposted builds | 7 |
| LIBRARY ideas | 20 |
| Reference | 17 |
| External FYP | 5 |
| External desire/utility cards | 25 |
| Tutorial-pinned | 75 |

Separately, 25 real-world event ingredients are NOT creatives. **37 examples were carded** in 28 card blocks.

## §8 Own posted
| Tier | Posts |
|---|---|
| WIN | P01 pink iPad; P02 Dre/CFA |
| MID | P03 McChicken; P08 Jalen (rate OK, reach low) |
| WEAK–MID | P05 MacBook |
| WEAK | P04 Maria part 2; P10 Jenny video |
| LOSER | P06 dasher nosy; P07 bf sequel; P09 Lindy |
| UNKNOWN | P11 Dre cent; P12 Cam |

Metrics are in the inventory with sources. None were invented.

## §9 Unposted / internal
- U01 Jalen part 2
- U02 McD broke
- U03 Terrence
- U04 Isaiah
- U05 Sarah iPad lock
- U06 lock McD
- U07 our_versions chats
- 20 LIBRARY ideas

No performance evidence exists for any of these.

## §10 Reference
- GE-001–004, GE-006–008
- @suziegotdauzi ×3
- @maddiequinn51
- @kelsitopsecret
- @ricc5ever memes
- Couple chat
- Lock-screen template
- Long-chat photos

Performance: qualitative only ("mega-viral" per the owner), with no numbers.

## §11 External FYP
Likes come from source cards:
- X01 Coach "money comes back": 421.5K
- X02 "swipe again": 136.2K
- X03 Marriott: 29.2K
- X04 Vinted biceps: 18.7K
- X05 math meme: 11.4K

## §12 External desire/utility
25 cards with metrics only (meal prep up to 41.7M views, soft glam, Amazon, gift baskets, Target hauls, Uber Eats). **No media or comments are on disk.**

## §13 Tutorial-pinned
- 75 unique posts, all with covers.
- 17 comment threads fetched: 16 non-empty, 1 returned 0 (aubreyvera4).
- The S6 identity/method shell is useful. Price-only shells (S4/S5) are not usable for us.

## §14 Excluded
- Pipeline-generated concepts (viewer-state, commercial-occupation, benchmark concepts)
- Agent browser screenshots
- Unrelated-project images (skincare WIP, persona selfies, Nintendo/Target refs)

All are listed in inventory §G.

## §15 Comment evidence: three classes kept separate
- **CAPTURED ORGANIC:** P01 (18 comments), P02 (15+), P03, P05, and tut-pinned top comments.
- **CAPTURED SUSPECTED-SEEDED:** the many 0–2-like "tried the method, worked" and handle-plug comments in S6 threads.
- **SYNTHETIC (predicted):** only where noted, and never counted as evidence.

## §16 Example cards
`VIRAL_CREATIVE_EXAMPLE_CARDS.md`. Every field from the brief is filled. Slide-by-slide breakdowns are given for every visual item.

## §17 Mechanic taxonomy
`VIRAL_STORY_MECHANIC_TAXONOMY.md` contains:
- 14 story mechanics (E-…)
- 5 commerce-integration mechanics, including the anti-patterns METHOD-HANDOFF and FLEX
- 4 desire/utility mechanics (D-…)
- 7 surface-grammar rules (G-…)

## §18 Swap tests
Six documented. These survive object, relationship, surface and no-discount swaps:
- MISHAP+KINDNESS
- RULE-DEFIANCE
- MONEY-ASK
- ABUNDANCE-UNDER-CONSTRAINT

These fail: FLEX and METHOD-HANDOFF.

**Real-data note:** the P05 object swap with plot copying failed. The P08 beat copy kept its rate but lost reach.

## §19 Psychology bank
`VIRAL_PSYCHOLOGY_PATTERN_BANK.md` has 15 patterns. Each has when-it-works, needs, kills, false positives and supporting evidence.

The core five (judgment, outcome desire, open question, proof demand, method gap) align with the protected CAS engine vocabulary. The remaining ten are additions:
- identity
- social-rule violation
- absurdity
- fairness
- kindness
- complicity
- audit
- replication
- envy/flex
- ad-suspicion

## §20 Winner/loser key findings
`WINNER_LOSER_CONTRAST_LIBRARY.md`, pairs C1–C7.
- The surfaces (order screen, electronics, iMessage, porch photo) do NOT predict the outcome.
- What predicts it:
  1. a viewer job that exists without the discount
  2. the price never mentioned by any character
  3. a reveal withheld for at least one slide
  4. mechanic novelty

## §21 What comments prove
- **P01:** the largest comment is kindness (96.4K), and the discount was *discovered* (22.8K). The story carried the deal.
- **P02:** side-taking plus price audit.
- **P03:** tip fairness turned against the narrator.
- **P05:** method-only engagement.
- **P07:** 0 comments, so no viewer job existed.
- **Tut-pinned:** organic heat goes to relationship and price, not method.

## §22 Generation grammar
`SYNTHETIC_STORY_GENERATION_GRAMMAR.md` covers:
- slots A–I
- 10 combination rules
- separate Family I and Family D grammar
- 5 originality operators
- a premise-card-only output

## §23 Originality and force check
`ORIGINALITY_AND_FORCE_CHECK.md` covers:
- copy-distance (pass at ≥4; automatic fail on reused lines, names, amounts, jokes or objects, and on burned names/kits)
- force score F1–F9 (forward at ≥7)
- auto-rejects R1–R9
- forced-premise checks FP1–FP4

## §24 Generator spec and pipeline position
`SYNTHETIC_STORY_GENERATOR_SPEC.md`. The generator sits beside the protected scouts as a labeled FICTIONAL/STAGED source for CAS step 2 (gravity). CAS and all existing gates run unchanged. The force score is an internal self-check, **not** a new gate, which respects the CAS rule "no downstream viral gate".

## §25 OPEN QUESTION: STOP + ask (not acted on)
CAS step 1 says "Scout reality". Should FICTIONAL/STAGED gravity cards be formally accepted as CAS input?
- **Option (a), assumed default:** pass them through CAS unchanged.
- **Option (b):** the user authorizes a one-line CAS amendment.

**I did not edit CAS.**

## §26 Corpus sufficiency (decided after the inventory)
**SUFFICIENT for v0 (Family I). NEEDS TARGETED, NON-BLOCKING EXPANSION** for Family D and for out-of-sample calibration. Details: `CORPUS_SUFFICIENCY_AND_GOOGLE_AI_QUESTION.md`.

## §27 Missing types (~30–45 useful examples)
1. Family D slideshows with slides and comments (8–12)
2. Beauty/home story-led winners with comments (5–8)
3. External story-carousel losers (5–10)
4. P05 and P07 missing slides
5. Comment text for P04, P06 and P08
6. Notes/Snapchat/camera-roll-led stories (3–5)
7. Clean, non-seeded tut-pinned comments

## §28 Google AI
The local audit was done first. Nothing is blocking. An optional question for gap 1 is drafted in the sufficiency file. **NOT SENT.**

## §29 Skill authoring
I read the skill-authoring guide (`/home/box/agent-data/managed-skills/skills/skill-authoring/SKILL.md`). The draft is at `skill_draft/synthetic-story-generator/SKILL.md` and contains:
- name + description frontmatter
- hard rules
- pattern-bank references
- procedure
- card schema
- known limits

It does not modify any protected skill and outputs premise cards only.

## §30 Skill install status
**BLOCKED / NOT INSTALLED.**
- No UpdateSkill tool is exposed to this executor. `GetDynamicTools` lists only cursor-github, cursor-origin and a Finance namespace that needs auth; a pattern search for "skill" returns nothing.
- I did not hand-write into `workflows/`. The guide says to manage skills through UpdateSkill.
- **Parent action:** call UpdateSkill (cursor namespace), action "write":
  - name: `synthetic-story-generator`
  - description and body: from the draft file

## §31 Generation test A–F
`generation_test/GENERATION_TEST_A_TO_F.md`, static and sandboxed. No assets, prices or posting.

| Input | Forwarded | Notes |
|---|---|---|
| A (no object) | A1, A2 | |
| B (karaoke machine) | B1; B2 after rework | |
| C (mundane) | C1 (after a copy FAIL on the first draft); C2 Family D | |
| D (console) | D1; D2 deprioritized | The FLEX control was rejected |
| E (food) | E1 | E2 sent to REWORK |
| F | F1 beauty, F3 fashion; F2 home (Family D, low confidence) | |

Five control premises were rejected by the filters.

## §32 Blind contrast test
`generation_test/BLIND_CONTRAST_TEST.md`. Pseudo-blind and in-sample.

| Example | Force | Outcome of the check |
|---|---|---|
| Pink iPad | 10 | forward |
| Dre/CFA | 10 | forward |
| MacBook | 9 | FAILS copy-distance |
| McChicken | 8 | REJECT via R6 (tip) |
| TP002 boo basket | 8 | forward (Family D) |
| TP001 price-only | 6 | R7, unusable for us |
| Boyfriend sequel | 2 | reject |
| Dasher nosy | 2 | reject |

Winners rank above losers. Force alone is insufficient; copy-distance and the auto-rejects are required.

## §33 YES/NO answers
| Question | Answer |
|---|---|
| A no-object | YES |
| B interesting object | YES |
| C mundane | YES |
| D high-desire without flex | YES |
| E food without burned kit | YES |
| F beauty | YES |
| F fashion | YES |
| F home | YES, low confidence |
| Family D separated | YES |
| No plot copying | YES |
| Premise-only | YES |
| Labeled FICTIONAL/STAGED | YES |
| Blind test winners > losers | YES (in-sample) |
| Force alone sufficient | NO |
| Valid predictive test | NO |
| Protected skills touched | NO |
| Skill installed | NO (blocked) |
| Google AI sent | NO |

## §34 Risks and limits
- Only 2 own winners, so the rubric is over-fit risk. Re-weight after 10 new posts.
- Family D is uncalibrated.
- Tut-pinned comments are contaminated by suspected seeding.
- Some reposted tut-pinned footage is stolen.
- Account and time confounds in the pairs.
- P04, P05 and P07 slides are incomplete on disk.

## §35 Hash end check
END hashes taken 2:26 PM ET (`_hashes_end.txt`). Compared on the 14 hash lines: **MATCH**.

## §36 Next steps and file index
**Next steps:**
1. The parent installs the skill via UpdateSkill from the draft.
2. The user answers the §25 CAS question.
3. Run a true blind test: score the next 5–10 premises *before* posting, then compare.
4. Collect the §27 gaps (start with Family D slides+comments and the P05/P07 slides).
5. Forward 2–3 Family I cards (e.g. A1, D1, F1) into CAS as staged gravity when origination is requested.

**Files:**
- `VIRAL_CREATIVE_CORPUS_INVENTORY.md`
- `VIRAL_CREATIVE_EXAMPLE_CARDS.md`
- `VIRAL_STORY_MECHANIC_TAXONOMY.md`
- `VIRAL_PSYCHOLOGY_PATTERN_BANK.md`
- `WINNER_LOSER_CONTRAST_LIBRARY.md`
- `SYNTHETIC_STORY_GENERATION_GRAMMAR.md`
- `ORIGINALITY_AND_FORCE_CHECK.md`
- `SYNTHETIC_STORY_GENERATOR_SPEC.md`
- `CORPUS_SUFFICIENCY_AND_GOOGLE_AI_QUESTION.md`
- `skill_draft/synthetic-story-generator/SKILL.md`
- `generation_test/GENERATION_TEST_A_TO_F.md`
- `generation_test/BLIND_CONTRAST_TEST.md`
- `_hashes_start.txt`, `_hashes_end.txt`
- `_w/` (scratch: image index, contact sheets)
