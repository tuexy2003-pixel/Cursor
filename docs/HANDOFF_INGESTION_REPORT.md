# Handoff ingestion report

Snapshot: `source_snapshots/2026-10-05/`
Checksums: `source_snapshots/2026-10-05.SHA256SUMS` (111 files)
Archive: `handoff_cursor_core.zip` (manifest version `handoff-2026-10-05-ext1`, generated 2026-10-05)
Inspection date: 2026-10-06
The snapshot directory is read-only. This report does not modify it.

## What was found

The core archive is a creative operating method, not an application. It contains:

- 15 Markdown workflow skills under `skills/*/SKILL.md`, plus `skills/live-heat-scout/QUERY_HYGIENE_PLAYBOOK.md` as a supporting playbook, not a 16th skill.
- One current Target story lock: `story_locks/TARGET_chore_stuff_STORY_LOCK_current.md`.
- Two related specs that are older than that lock: `story_locks/TARGET_CHORE_STUFF_TRANSACTION_MATH_SPEC.md` and `story_locks/BENCHMARK_SURFACE_TRANSACTION_SPEC.md`.
- Engineering and authority documents listed in `SYSTEM_MANIFEST.json` `engineering_docs`.
- `MEMORY_ONLY_KNOWLEDGE.md`, an export of decision-relevant agent memory, explicitly not the full older memory (~545 facts not enumerated).
- Structured JSON that is evidence or contract metadata, not a database: `SYSTEM_MANIFEST.json`, `SKILL_IO_CONTRACTS.json`, `ASSET_INDEX.json`, `GOLDEN_REGRESSION_TESTS.json`, one historic source card, one iOS 26 template spec, one early carousel spec draft.
- Legacy Python under `engineering_source/`. The engineering inventory marks these renderers and catchup scripts as unused for current finals.
- Reference prose under `reference_docs/`, including a viral-story research corpus and older playbooks.
- Target bank text manifests and one contact-sheet JPEG under `manifests_existing/`.
- No package, service, test suite, Dockerfile, or persistent database for the creative pipeline.

`README.md` inside the snapshot mentions an `examples/` folder of final v6 slides, bases, ingredients, and a stale list. That folder is not in this core archive. Binary visual examples were split into supplemental archives that are not present. Asset-index rows claim `exists: true` against historical `/workspace/creative-pipeline/...` paths. Those binaries are absent here. Presence in the original environment is not the same as presence in this snapshot.

## What appears authoritative

Authority is domain-specific. It is not last-write-wins. The ordering in `AUTHORITY_AND_PRECEDENCE.md` is:

1. Latest explicit human correction.
2. Latest human-approved story lock, for creative-specific values.
3. Current active workflow skill, for system behavior.
4. Approved account or program configuration. No account config file exists. Account state lives in `ACCOUNT_STATE_TODAY.md` and `MEMORY_ONLY_KNOWLEDGE.md`.
5. Reference-bank evidence, for native visual structure.
6. Current generated asset.
7. Older story-lock versions.
8. Memory notes.
9. Stale or old generated assets.
10. Deprecated rules.
11. Historical examples.

For this snapshot, creative story values for the Target benchmark come from `story_locks/TARGET_chore_stuff_STORY_LOCK_current.md`. The historical path cited in the manifest is `/workspace/creative-pipeline/outputs/chore_stuff_target_20261005_v4/STORY_LOCK.md`. That path is provenance. The copied lock in `story_locks/` is the readable source in this archive, and its header says it is the authoritative story truth as of the 2026-10-05 continuity update.

Active system behavior comes from the 15 skills, with these statuses from `SYSTEM_MANIFEST.json`:

| Skill | Status |
| --- | --- |
| story-development | ACTIVE |
| production-spec-qa | ACTIVE |
| ios-26-production-normalization | ACTIVE |
| visual-surface-acquisition | ACTIVE |
| find-purchase-screens-on-pinterest | ACTIVE |
| commercial-aware-synthesis | ACTIVE, frozen V1.2 |
| synthetic-story-generator | ACTIVE |
| adaptation-blitz-match | ACTIVE, frozen gates |
| story-conflict-scout | ACTIVE |
| object-culture-scout | ACTIVE |
| live-heat-scout | ACTIVE |
| commerce-world-mapper | SUPPORTING |
| source-card | SUPPORTING |
| chat-story-slideshow | SUPPORTING |
| getting-started | LEGACY |

`SKILL_IO_CONTRACTS.json` repeats those statuses and marks every contract `informal_current_contract: true`.

## What is historical

These lose to the current skills and the current lock:

- `reference_docs/SYSTEM_PLAYBOOK.md`
- `reference_docs/CATCHUP.md`
- `reference_docs/HANDOFF_LATEST.md`
- Older format guidance of 1080×1920 / 9:16, including `skills/getting-started/SKILL.md`
- Peek-first as a universal S1 rule
- Retired Messages bases (Refinery29 iOS 13, Gboard)
- `logs/creative-tests.jsonl` and early candidate specs
- Legacy Pillow UI rebuild scripts. Freehand retailer reconstruction is a known failure, not a production method.
- `manifests_existing/00_READ_FIRST_CURRENT_HANDOFF.md` still shows Slide 1 dialogue that includes “doing a quick Drive Up”. That phrase is a documented rejection. The current lock’s dialogue does not use it.

## What is stale

Stale relative to the current Target lock, not deleted:

- Floating hook “my birthday is literally tomorrow 😭”. The lock supersedes it with “my birthday is literally today 😭”.
- AirPods 4. The lock uses Apple AirPods 5 at $129.99.
- Pickup copy “Wed, Oct 23” on older bases. The ledger says “Pick up by Wed, Oct 7”.
- The transaction math spec’s four-item basket and totals: subtotal $12.98, discount −$8.00, tax $0.35, total $5.33. The current lock’s basket includes AirPods 5 and totals $142.97 / −$125.00 / $1.26 / $19.23.
- The surface spec’s “four lines, optional fifth not used” item plan.
- Asset paths listed in the lock’s STALE ASSETS section (v1–v5 attempts). The image files themselves are not in this core archive.

## What is implemented

Implemented today, outside this repository’s new software:

- 15 Markdown skills interpreted by an LLM.
- Manually edited story-lock files.
- Manual stale lists.
- Target reference-bank metadata and DoorDash reference notes.
- Manual ChatGPT image editing, Pinterest search, and occasional local PIL checks.
- Viral-story research documents and a synthetic-story generator spec.
- Informal performance numbers in memory and review docs.

## What is only planned

`IMPLEMENTED_VS_PLANNED.md` and `SYSTEM_MANIFEST.json` agree that these did not exist as systems:

Creative Genome, Account DNA, experiment registry, performance ingestion, comment clustering against predicted doors, novelty or fatigue tracking, provenance registry, versioned creative records, multi-account learning, holdout evaluation, automated deterministic validation, dashboards, and orchestration.

Partial only: comment-door maps inside story development, folder-level provenance notes, v1–v5 folders, a few remembered view counts, and manual QA checklists.

## What must remain model-led

From `COSTLY_VS_DETERMINISTIC.md` and the skills:

- Premise quality, Family I versus Family D, and gate judgments.
- Whether dialogue sounds like a person texting.
- Hook strength and whether an overlay adds context.
- Propulsion diagnosis and the smallest causal-beat repair.
- Viral texture, contrivance, and life-world fit.
- Visual-native judgment and ambiguous route choice.
- Image editing itself.
- Creative interpretation of comments and performance.

Frozen gates in commercial-aware synthesis and adaptation-blitz-match stay prose policy. They are not rewritten into booleans.

## What should become deterministic

- Story-lock versioning, approval stamps, diffs, and stale marking.
- Arithmetic, weekday checks, and structured timeline order.
- Aspect ratio against a scoped target, not an eternal global constant.
- Product, quantity, variant, and color checks where structured values exist.
- Rights and export gates.
- Provenance indexing.
- Experiment, performance, and comment storage.
- Approval-gate presence.
- Current-lock precedence over older assets.

## Contradictions found

1. **Floating-hook example versus current lock.** `skills/production-spec-qa/SKILL.md` gives “my birthday is literally tomorrow 😭” as a good floating-hook example. The current story lock, `CURRENT_STATE.md`, `MEMORY_ONLY_KNOWLEDGE.md`, `PRINCIPLES_VS_HEURISTICS.md`, and the regression overlay example use “my birthday is literally today 😭”. The lock wins for this creative. The imported skill text stays unchanged. A later working policy version may update the example. The snapshot must not be edited to hide this.
2. **Transaction math spec versus current lock.** The math spec locks a four-item basket and $5.33 total. The story lock locks five items, AirPods 5, and $19.23. Creative values follow the story lock. The math spec remains a historical pre-production artifact. Its arithmetic identity (`12.98 − 8.00 + 0.35 = 5.33`) is internally consistent and is not the current creative.
3. **Surface spec and bank read-first versus lock.** Both still describe an earlier Slide 1 and a four-item order without AirPods. `00_READ_FIRST_CURRENT_HANDOFF.md` also uses the rejected line “doing a quick Drive Up”.
4. **Story-development stakes example.** The skill uses “birthday tomorrow” as a generic stakes illustration. That is not labeled as the current lock’s hook. It is a lower-severity overlap with the superseded hook, not a second source of story truth.
5. **Format.** Getting-started, the playbook, and catchup still mention 1080×1920. Production-spec-qa and the principles doc say 9:19.6. Production rules win. 9:19.6 is a current program preference, not a universal law of the engine.
6. **Asset existence.** `ASSET_INDEX.json` says `exists: true` for binaries that are not in this archive. Treat that as a claim about the original box filesystem.
7. **Abbreviated current-state dialogue.** `CURRENT_STATE.md` summarizes three thread beats. The lock contains five locked lines, including “grabbing stuff for the house rn” and “why would i look”. The lock is the full creative truth.
8. **Account configuration.** Precedence slot 4 has no file. Importing account notes does not create an approved config that outranks a later human correction.

## Source-of-truth relationships

| Domain | Source of truth in this handoff |
| --- | --- |
| Creative story values | Current approved story lock |
| System behavior | Active skills, after explicit human corrections |
| Native visual structure | Reference-bank evidence and approved bases |
| Research facts | Real sources only. Staged economics are labeled FICTIONAL/STAGED |
| Account lanes and life-world | Memory export and account-state notes, until a human-approved account record exists |
| Production format | Current production-spec-qa default, scoped, over older 9:16 docs |
| Rights | Explicit notes only. Unknown stays UNKNOWN. Pinterest pins are REFERENCE ONLY by skill rule |
| Regression behavior | `GOLDEN_REGRESSION_TESTS.json` (19 cases, T01–T18 including T03a and T03b) |

## Migration assumptions

- Historical absolute paths (`/workspace/creative-pipeline/`, `/home/box/agent-data/workflows/`) are provenance, not runtime dependencies.
- The 15 skills are preserved as versioned Markdown. They are not flattened into one prompt and not translated into hard constraints in this pass.
- Target and DoorDash are current commercial ecosystems for MyDashPerks, stored as program configuration, not as schema types.
- The 15–20 life-world, account lanes, and the current Target dialogue, prices, and products are scoped. They are not global invariants.
- Supplemental visual archives can be imported later by original relative path and hash.
- No autonomous posting, messaging, ordering, purchasing, or checkout is in scope.
- ChatGPT image-edit model version is UNKNOWN.
- Performance numbers are stored only when the handoff states them. Maria McChicken, the Brooke sequel, and “Dasher got nosy” view counts stay null.
- One viral post does not rewrite Account DNA.
- Deterministic validators return `MODEL_REVIEW_REQUIRED` or `HUMAN_REVIEW_REQUIRED` when the case needs taste, vision, or a live retailer check. They do not return a fake pass.

## Missing information

- Supplemental example archives and the `examples/` binaries.
- Full agent memory beyond the exported subset.
- Exact ChatGPT model version.
- TikTok posting tooling (manual; UNKNOWN).
- Contents of `/workspace/avatar-cast`.
- DoorDash round 2–4 folder contents.
- Teammate-bot roles beyond one-line descriptions.
- Most post-level metrics, comments, and saves.
- Whether every reference-bank image is a cleared base or reference-only. The index does not state rights per file. Default is UNKNOWN unless the skill or notes are explicit.
- A formal account ID scheme. Names in the account-state note are the only clear account labels.

Low-value gaps are recorded as UNKNOWN and do not block the data model.

## Path and environment issues

- The handoff host was a shared Linux box, user `box`, timezone America/New_York, roots under `/workspace/creative-pipeline` and `/home/box/agent-data/workflows`.
- This repository runs elsewhere. Storage roots are configurable.
- `zip` was not part of the creative pipeline; that constraint applied to the old box, not to this repo.
- Env var names that existed on the box: `SCRAPECREATORS_API_KEY`, `APIFY_TOKEN`, `FISH_API_KEY`. No secret values were in the archive. Fish Audio is not part of the carousel pipeline (UNKNOWN).
- No virtualenv existed in the creative pipeline. Legacy scripts mention one.

## Known discrepancy to preserve

Recorded, not repaired in the snapshot:

`skills/production-spec-qa/SKILL.md` still contains the good-example line “my birthday is literally tomorrow 😭”.
The current approved story lock uses “my birthday is literally today 😭”.
The story lock wins.
