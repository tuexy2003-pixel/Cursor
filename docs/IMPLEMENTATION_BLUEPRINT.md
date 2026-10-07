# Implementation blueprint

This blueprint follows `docs/HANDOFF_INGESTION_REPORT.md`. The creative policy stays in versioned Markdown. Software versions, validates, and retrieves it.

## 1. What the handoff contains

A Grok-interpreted skill system for staged TikTok photo carousels, currently centered on MyDashPerks, with Target and DoorDash as the only commercial ecosystems in use. There is one human-approved Target story lock, a locked-but-unproduced DoorDash benchmark, 15 skills, 19 regression cases, asset metadata without most binaries, and a large historical prose layer. Details, contradictions, and authority are in the ingestion report. The transaction math spec’s $5.33 basket does not override the story lock’s $19.23 basket.

## 2. Repository architecture

```
apps/api/                process entry notes; the API lives in src/creative_os/api
apps/web/                Next.js operator UI
src/creative_os/
  api/                   FastAPI routes
  models/                SQLAlchemy models
  schemas/               Pydantic documents
  services/              story-lock versioning, staleness, context assembly
  validation/            deterministic checks and regression runner
  importers/             idempotent handoff import and story-lock parser
  providers/             capability interfaces and explicit stubs
alembic/                 migrations
tests/
docs/
source_snapshots/2026-10-05/    immutable import
storage/                 local sqlite and later file blobs (gitignored db)
```

Python packages stay in one installable project so migrations, the importer, and the API share one model layer. Module boundaries are the packages above, not separate publishable libraries. A monorepo is enough: one database, one operator, one importer.

## 3. Stack

| Piece | Choice | Why |
| --- | --- | --- |
| API | Python 3.12, FastAPI, Pydantic v2 | Typed schemas, boring HTTP, matches the requested stack |
| ORM | SQLAlchemy 2 | Explicit models, SQLite now, PostgreSQL later |
| Migrations | Alembic | Repeatable from a clean database |
| DB | SQLite file under `COS_DATABASE_URL` | Local development. JSON, strings, numerics, and UUID strings stay portable to PostgreSQL |
| UI | Next.js, React, TypeScript | Operator pages over the API |
| Tests | pytest | Domain and import behavior |
| Lint | ruff | Format and lint |
| Types | mypy on `src/creative_os` | Catch contract drift |

No Grok SDK. No image-provider SDK. Provider calls are stubs that return `NOT_IMPLEMENTED`.

## 4. Domain model

Normalized where queries and integrity matter. Prose stays attached to the artifact instead of being shredded into flags.

- **Program, Account, Campaign, Ecosystem.** Ecosystem is a generic commercial system (Target, DoorDash today). Programs link to ecosystems. Accounts belong to a program and carry lanes as observations, not as columns named after people.
- **Creative.** Points at `current_approved_story_lock_version_id`. Status describes lifecycle (`concept`, `locked`, `in_production`, `approved_final`, `not_produced`).
- **StoryLock** identity plus immutable **StoryLockVersion** documents.
- **ApprovalEvent** for human decisions. Approval is not an in-place edit of an old version.
- **SkillArtifact / SkillVersion.** Markdown, hash, status, scope, source path.
- **PolicyRule.** Scoped prose or structured preference. Rule kind is `INVARIANT`, `HEURISTIC`, `PREFERENCE`, or `LOCKED_VALUE`.
- **Asset, AssetRelation, ReferenceBank, StaleArtifactRecord.** Roles: `BASE`, `INGREDIENT`, `REFERENCE`, `EVIDENCE`, `EXAMPLE`.
- **RegressionTest, BenchmarkCreative.**
- **ValidationRun / ValidationResult.**
- **ModelProvider / ModelRun.** Historical versions may be UNKNOWN.
- **CreativeGenome / GenomeFacet.** Facets are rows, not one opaque blob.
- **AccountDnaProfile / AccountDnaObservation.** Evidence kind is `HUMAN_SET_CONSTRAINT`, `HISTORICAL_OBSERVATION`, or `MODEL_INFERRED_BELIEF`.
- **Experiment / ExperimentVariant.**
- **Post / PerformanceSnapshot.**
- **Comment / CommentCluster / CommentDoor / CommentDoorMapping.**
- **Slide projection, line items, continuity entries, viral-texture details.** Projections of a story-lock version for queries. The version’s `content_json` is canonical.
- **MechanicObservation.** Frequency and recency of a dimension value. No viral-fatigue score.
- **SourceArtifact.** Import path, hash, role in the snapshot.

Not separate tables: birthday, AirPods, paper towels, cake mix, Peek, or a retailer-specific order screen. Those are values inside generic line items, dialogue, and facets.

## 5. Schema overview

Identifiers are UUID strings. Money inside story documents uses decimal strings. Timestamps are timezone-aware UTC.

Immutable story-lock versions reject updates to `content_json`, `content_markdown`, and `content_hash`. Supersession is a pointer on the new version (`supersedes_version_id`) and on the creative. Old rows stay byte-stable.

`content_json` follows `StoryLockDocument`: title, label, hook, floating hook, propulsion fields, dialogue turns, line items, economics, story date, slides, continuity entries, comment doors, viral-texture details, stale notes, and an `extra` object for unparsed source text. Missing fields stay null.

Assets store original source paths as provenance. Runtime files, when present, live under the configured storage root.

## 6. Rule scope

Every policy rule has:

- `scope_level`: `GLOBAL`, `PROGRAM`, `ACCOUNT`, `CAMPAIGN`, `CREATIVE`
- `scope_id`: null only for global
- `rule_kind`: `INVARIANT`, `HEURISTIC`, `PREFERENCE`, `LOCKED_VALUE`

Global invariants seeded from the handoff, as prose plus a stable code:

- Human corrections outrank automation.
- Proof only proves what is literally supported.
- Rights and provenance are retained.
- Stale artifacts do not override current approved truth.
- Human approval gates stay authoritative.
- A suitable approved base is edited, not freehand-reconstructed.

Program preferences, not global laws:

- MyDashPerks money path as a quiet discount line.
- Current ecosystems Target and DoorDash.
- Current final aspect 9:19.6.

Account observations:

- Maria food/couples, Sarah and Brooke electronics, 15–20 life-world as a present preference.

Creative locked values live on the story-lock version, not as global rules. The importer may also store a creative-scoped note that points at the lock so section D of the principles doc is not dropped.

## 7. Story-lock versioning

`StoryLock` is the identity. `StoryLockVersion` is an append-only document.

Approving a human correction:

1. Load the current approved version. Do not modify it.
2. Copy the document and apply the requested field change.
3. Insert a new version with `supersedes_version_id`, reason, approver, and content hash.
4. Insert an `ApprovalEvent` with status `APPROVED`.
5. Point the creative at the new version.
6. For assets bound to the previous version, insert `StaleArtifactRecord` rows. Do not delete assets or rewrite their bytes.
7. Export Markdown from the structured document so the database is not the only reading surface.

Diffs are field-level comparisons of the two documents.

## 8. Policy and skill versioning

Each `SKILL.md` imports as one skill artifact and one version: raw Markdown, sha256, source path, manifest status, effective time from the snapshot date. Re-import of the same hash does not insert another version.

The production-spec-qa “tomorrow” example is preserved in the imported version. This build does not publish a silently “corrected” skill as if a human had approved it. The discrepancy is a migration note. A future human-approved skill version can change the example.

Additional skill files, such as the live-heat query playbook, import as related source artifacts and are linked from the skill, not treated as extra skills.

## 9. Asset and provenance architecture

Each indexed asset records original path, role, ecosystem, story key, approved flag, stale flag from the index, and `present_in_snapshot` computed by looking for a copied file. Hash is set only when the file is in the snapshot. Missing binaries do not get invented hashes.

`AssetRelation` records parent, base, ingredient, reference, and evidence links when the handoff states them. Unknown links stay absent.

Editing method and provider stay null until a run exists. Recursive-edit validation uses the relation chain: a new edit must name the original base, not an intermediate derivative, when that chain is recorded.

## 10. Rights model

Statuses: `CLEARED`, `USER_OWNED`, `LICENSED`, `PUBLIC_DOMAIN`, `REFERENCE_ONLY`, `UNKNOWN`.

Import rules:

- The user’s own Messages keyboard base is `USER_OWNED` because the index and memory export say it is the user’s screenshot.
- Pinterest-derived pins are not in the asset index as individual files. The skill rule remains a global invariant: unknown-rights pins are reference-only.
- GIGAZINE packaging is `UNKNOWN`, not licensed. The note records the source.
- Everything else in the index is `UNKNOWN` unless the row or skill is explicit.

Export validation:

- `REFERENCE_ONLY` cannot ship as a production `BASE` (`FAIL`).
- `UNKNOWN` cannot silently ship as a production `BASE` (`HUMAN_REVIEW_REQUIRED`).
- Cleared-class statuses can pass the rights gate.

No legal conclusions are inferred from filenames.

## 11. Validation architecture

Result statuses: `PASS`, `FAIL`, `WARNING`, `NOT_APPLICABLE`, `MODEL_REVIEW_REQUIRED`, `HUMAN_REVIEW_REQUIRED`, `NOT_IMPLEMENTED`.

Deterministic checks:

| Check | Behavior |
| --- | --- |
| Arithmetic | `subtotal - discount + tax == total` at cent precision. Optional line-item sum versus subtotal |
| Weekday | Civil date versus claimed weekday |
| Timeline | Structured clocks on slides must be non-decreasing when both parse. Relative “tomorrow” plus a same-day payoff without a transition fails |
| Aspect ratio | Compare width/height to the scoped target. Default program target is 9:19.6 with absolute tolerance 0.008 so 1206×2622, 851×1849, and 853×1844 pass and 1080×1920 fails |
| Current lock | Structured product identity on an asset must match the current lock |
| Stale assets | Asset bound to a non-current version should have a stale record |
| Rights export | See rights model |
| Approval | A production-ready creative needs an approval event on the current version |
| Provenance | Role, rights, and original path required. Missing hash when the file is absent is a warning |
| Version consistency | Creative pointer matches an existing version of its lock. Superseded version is not the pointer |
| Product consistency | Model, generation, quantity, variant, color, pack count when those fields are present on more than one slide |

Dialogue naturalness, hook choice, visual native-ness, and “is this detail contrived?” are not deterministic passes.

## 12. Golden-regression migration

All 19 JSON cases import as `RegressionTest` rows with the original id, input, expected decision, and source rule.

| Ids | Runner |
| --- | --- |
| T16 math, T17 weekday, T14 aspect | Deterministic unit checks |
| T05 stale reference date, T04 continuity, T06 current lock, T18 recursive edit | Deterministic on structured fixtures |
| T13 product generation | `HUMAN_REVIEW_REQUIRED` unless a logged live check is present. Software does not call Target |
| T01, T02, T03a, T03b, T07, T08, T09, T10, T11, T12, T15 | `MODEL_REVIEW_REQUIRED`. Expected decision is stored and shown. The runner must not return `PASS` |

T03a and T03b stay separate so the firewall and the story-motivated exception are not collapsed.

## 13. Handoff importer

`python -m creative_os.cli import-handoff` reads `COS_SNAPSHOT_ROOT`.

It ingests:

- Every file as a `SourceArtifact` (path, hash, size).
- Skills and the query-hygiene playbook.
- Principles sections as scoped policy rules.
- The Target story lock through the Markdown parser. Fields that do not match stay in `extra` or raw Markdown. The parser does not invent values.
- DoorDash onions as a creative with only the explicit overlay, product, missing modifier, and not-produced status. No prices.
- Regression tests.
- Asset index metadata.
- Benchmark rows. Unknown metrics stay null. Current unposted benchmarks are holdouts.
- Named accounts and performance observations that have explicit numbers.
- Program MyDashPerks and ecosystems Target and DoorDash.

Idempotency key is source path plus content hash. A second import updates nothing and inserts nothing for unchanged artifacts.

Supplemental archives later: the importer accepts an additional root and matches relative paths already stored as original paths, setting hash and `present_in_snapshot` without duplicating the asset identity.

## 14. Creative Genome

A genome belongs to a creative version or creative. Facets are rows:

`dimension`, `value`, `source`, `assignment` (`human_set` or `model_inferred`), `confidence` (null if not inferred), `created_at`.

Initial dimensions are an open vocabulary, including the list in the mission: family, hook type, propulsion type, comment doors, commerce integration, ecosystem, continuity shape, and the rest. Import seeds only facets that the lock or principles state in plain language, for example commerce relation `SECONDARY` and “story works without economics: yes”. It does not invent hook-type taxonomy codes.

## 15. Account DNA

Versioned profile per account. Observations carry evidence kind, confidence, sample size, date range, and source path.

Seeded observations:

- Lane assignments as human-set constraints from the account-state note.
- Brooke 2.3M, Maria Chick-fil-A 338.2K, Sarah MacBook 150.5K as historical observations with sample size 1.
- No model-inferred belief that an account “wins with overslept DoorDash” as a law. That pattern can be stored later as an inferred belief with low sample size, and this import does not create it.

## 16. Experiments, performance, comments

Tables exist. The importer does not invent experiments or comment dumps that are not in the core archive. APIs accept manual performance snapshots and comments. Metrics that are absent stay null. Raw payload can be stored. Predicted comment doors import from the Target lock’s primary and secondary doors. Actual comments are empty. Mapping status stays `NOT_IMPLEMENTED` until comments exist. Novelty reporting aggregates `MechanicObservation` by dimension with count and latest timestamp. There is no score.

## 17. Provider abstraction

Capabilities: `creative_reasoning`, `research`, `web_search`, `visual_search`, `image_editing`, `image_generation`, `vision_qa`, `comment_interpretation`, `performance_interpretation`.

`ModelProvider` rows record historical tools (Grok as creative reasoning, ChatGPT web as image editing, ScrapeCreators, Apify) with model version `UNKNOWN` where the handoff says so. `StubProvider.run` returns `NOT_IMPLEMENTED`. Context assembly selects global invariants, program preferences, the account, the campaign, the current creative, the current lock, holdout-excluded benchmarks, and recent mechanic counts, with explicit limits. It does not dump the snapshot.

Phase 6 does not execute providers.

## 18. UI routes

| Route | View |
| --- | --- |
| `/` | Status, import counts, authority reminder |
| `/accounts` | Accounts and DNA summary |
| `/campaigns` | Campaigns |
| `/creatives` | Creative list |
| `/creatives/[id]` | Lock, versions, diff, slides, doors, economics, assets, validation, approvals |
| `/assets` | Provenance and rights |
| `/references` | Reference banks |
| `/experiments` | Registry |
| `/posts` | Posts and snapshots |
| `/comments` | Doors, clusters, mappings |
| `/benchmarks` | Benchmarks and regression cases |
| `/policies` | Skills and scoped rules |
| `/runs` | Model runs and validation runs |

The UI reads the API. It does not embed a model.

## 19. Phased plan

| Phase | This build |
| --- | --- |
| 0 | Snapshot, docs, app skeleton, migrations, importer, baseline counts |
| 1 | Versioned locks, approvals, stale marking, acceptance test |
| 2 | Deterministic validators and regression runner |
| 3 | Genome, DNA, doors, texture, continuity, benchmarks stored beside skills |
| 4 | Experiments, posts, comments, mechanic history, manual ingest APIs |
| 5 | Operator UI for those records |
| 6 | Provider interfaces and context assembly only. No live model orchestration |

## 20. Migration risks

- Turning heuristics into hard failures. The runner keeps judgment cases on the model/human path.
- Promoting the Target lock or the 15–20 audience into global schema.
- Letting the math spec or the bank read-first overwrite the lock.
- “Fixing” the tomorrow example inside the snapshot.
- Treating `exists: true` as a local file.
- Automating checkout or posting. Not built.
- Re-editing from degraded outputs. The relation check only runs when the chain is recorded. Otherwise the result is `HUMAN_REVIEW_REQUIRED`, not a pretend pass.
- Frozen V1.2 gates. They remain skill text.

## 21. Acceptance criteria

- Snapshot hashes match the checksum file, and the snapshot cannot be written.
- 15 skills and 19 regression tests import once and stay unique on re-import.
- The current lock is readable as Markdown export and as structured fields that the source actually states.
- A human correction creates a new version, an approval, an updated pointer, a stale record on an older asset, and leaves the old version unchanged.
- Math, weekday, aspect, rights, approval, provenance, and lock-precedence tests pass.
- Judgment regression cases do not return `PASS`.
- API and UI start with documented commands.
- Unknown metrics stay null.

## 22. Discrepancies and ambiguities

See the ingestion report. The implementation assumption that changes the prompt’s “current math” picture: the pre-production math spec’s authoritative-looking $5.33 lock is superseded by the story lock’s $19.23 economics. Both are imported. Only the story lock is the creative pointer.

`AUTHORITY_AND_PRECEDENCE.md` names Tyrel as the human approver. Approval records use that name when the source says he approved, and `UNKNOWN` when the source does not name a person.

## 23. Prompt assumptions changed by the handoff

- “19 regression tests” is correct only if T03a and T03b both count. The file’s last id is T18.
- 9:19.6 is the current production default and a program preference. Config also accepts ChatGPT outputs around 851×1849 and 853×1844, not only 1206×2622.
- Getting-started is one of the 15 skills and is `LEGACY`. It is imported and is not an active production rule.
- The core zip does not contain the example binaries the snapshot README mentions.
- Commerce integration is inside the lock in the manual workflow, not a separate system.
- There is no account file to import. Accounts are reconstructed only from named personas in the account-state note.
