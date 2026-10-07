# v0.2 core integrity hardening

The preservation architecture from `v0.1.0-preservation-baseline` stays. This pass fixes integrity gaps found in the v0.1 source review. Provider execution is still `NOT_IMPLEMENTED`.

## Story lock canonical hash

Problem: `content_hash` mixed source-byte hashes and rendered Markdown. The v0.1 renderer omitted `commerce_relation` and most continuity, so a semantic change could leave the rendered text unchanged.

Old behavior: corrections used `model_copy(update=changes)` and hashed the lossy Markdown.

New behavior: `document_hash` is SHA-256 of deterministic canonical JSON (`model_dump(mode="json")`, sorted keys, compact separators, UTF-8). Imported `content_hash` and `source_hash` are unchanged. New versions also store canonical Markdown v2, which includes a structured JSON block so render then parse returns the same document. Historical handoff Markdown is not rewritten.

Migration: `c8d4e1a07b33` adds `document_hash` and backfills it from stored `content_json` through the same canonical function.

## Validation and nested patches

Problem: an invalid typed value could enter a story lock, and corrections only replaced top-level scalars.

New behavior: every correction builds a payload and calls `StoryLockDocument.model_validate`. A boolean `story_date` fails before a version is written. Patches use paths such as `/line_items/2/model`. `deep_diff` reports those paths for the UI, staleness, and review.

## Approval boundary

Problem: `POST /creatives/{id}/story-lock/corrections` trusted `actor` from JSON and immediately moved the approved pointer.

New behavior: the human route records `COS_OPERATOR_IDENTITY` and approves in one step. `POST .../story-lock/proposals` creates a `PENDING` version and does not move the pointer, even if `proposer` is the operator name. `POST .../versions/{id}/decision` accepts `APPROVE`, `REJECT`, or `NEEDS_CHANGES` as the configured operator. Approval of a proposal is an `ApprovalEvent` plus the pointer move. The proposal row stays immutable.

There is still no login system. Non-loopback hosts refuse to start.

## Selective staleness

Problem: every asset bound to the previous story lock became stale, including Target UI bases and product ingredients.

New behavior: `asset_lock_dependencies` records explicit field paths. A change marks an asset `STALE` only when a dependency path intersects a changed path. Bases and ingredients without a matching dependency stay current. An `EXAMPLE` with no declared dependency becomes `STALE_REVIEW_REQUIRED` instead of a silent assumption. The Target S1 final depends on the hook, dialogue, and slide 0. S2 and S3 depend on line items, economics or texture, and their slides.

## Deep diff

`document_diff` remains the top-level helper. `deep_diff` is the path-aware diff used by the story-lock diff endpoint and by staleness.

## Version immutability

Story lock versions now also reject updates to `document_hash`, `change_reason`, `approved_by`, `supersedes_version_id`, source fields, `version_number`, `story_lock_id`, and `approval_state`. Decisions live on `approval_events`. Self foreign keys were added for story-lock, skill, DNA, and stale-record succession where the database can express them.

## Source snapshots

Problem: `source_artifacts.relative_path` was globally unique, and a re-import could overwrite the hash.

New behavior: `source_snapshots` owns artifacts. Uniqueness is `(snapshot_id, relative_path)`. The same label with different bytes raises `SnapshotIntegrityError`. A new label creates a new snapshot. The 2026-10-05 snapshot is the first row.

## Policy versions and the resolver

`policy_rules` now record `supersedes_rule_id`, `source_skill_version_id`, `source_artifact_id`, `approval_state`, and `effective_to`. Imported rule text is not rewritten. The program copy of the money-path rule points at the superseded global row.

`resolve_policy` walks GLOBAL, PROGRAM, ACCOUNT, CAMPAIGN, and CREATIVE. The same code and kind resolve to the most specific applicable scope. Different invariant codes are all kept. A token budget can drop heuristics. It cannot drop an included invariant.

## Context compiler

`compile_context` is the dry-run package. `assemble_context` is only a short compatibility summary and is not the compiler. `GET /creatives/{id}/context-preview?stage=` returns the package: stage, lock, scoped policies, skills, approved DNA, the genome bound to the current lock, benchmarks that are not holdouts, account mechanic windows, reference metadata, doors, continuity, and items excluded for budget or stage. Each included item records source, scope, reason, version, and authority. The creative page shows the counts.

## Genome, DNA, mechanics, posts

A genome stores `source_story_lock_version_id`, `origin` (`HUMAN_SET` or `MODEL_INFERRED`), and `approval_state`. `Creative.current_genome_id` is the approved genome. Newest `created_at` is not authority.

`Account.current_approved_dna_profile_id` is the approved profile. A higher `version_number` with `PENDING` or `MODEL_INFERRED` does not become current.

Mechanic observations can store `account_id`, `post_id`, `story_lock_version_id`, and `genome_id`. Frequency is reported for the last 7 days, last 30 days, lifetime, and the last 10 published posts, plus a separate program-wide lifetime count. There is no fatigue score.

A post stores the story lock version, genome, and experiment variant it was published with. `post_assets` records the slides. A later lock does not retarget the post. Cross-account creative/post pairs are rejected in service code with a validation error.

## Experiments, performance, comments

A `SINGLE_VARIABLE` experiment must change only `variable_dimension`. Extra changed dimensions require `MULTIVARIATE`. `experiment_variant_posts` allows more than one post per variant.

Performance snapshots keep the raw `revenue` string. Typed `revenue_amount` and `revenue_currency` are stored only when the caller supplies them. `post_age_hours` is calculated when `published_at` exists. Missing metrics stay null.

`comment_cluster_members` links real comment rows. A door mapping is rejected when the door's creative, or its story lock, does not match the post.

## Review package

`test_snapshot_is_not_writable` skips when extraction leaves the tree writable. Checksums are the integrity gate. Visual tests are `full_assets` and skip when the supplement binaries are absent. `pytest -m core` is the portable command. The review zip includes `source_snapshots/2026-10-05.SHA256SUMS`, the core snapshot files those checksums name (including `manifests_existing/target_bank_v2_contact_sheet.jpg`), and omits the large supplemental image corpus.

## Database

Migration `c8d4e1a07b33` revises `b7c1a9e0d4f2`. It backfills the snapshot, document hashes, approval flags, genome lock binding, DNA pointers, and the explicit Target S1/S2/S3 lock dependencies. Indexes cover comments, performance, posts, assets, projections, doors, mechanics, genome facets, and DNA observations.

## Tests

`tests/test_integrity.py` covers the review cases: canonical hash, validation, round trip, deep diff, selective stale, approval boundary, snapshots, policy budget, DNA, genome binding, post binding, experiment isolation, cluster membership, and cross-creative doors. `tests/test_migration.py` upgrades a populated v0.1-shaped database and checks the lock text and source hash survive.

## Remaining limitations

- No operator login. Loopback plus `COS_OPERATOR_IDENTITY` is the trust boundary.
- Proposal rows stay `PENDING` in the version table after approval. The pointer and the approval event are the decision.
- Dependency paths for the Target finals are explicit. Other deliverables without a path become `STALE_REVIEW_REQUIRED`.
- Unknown rights stay `UNKNOWN`.
- 17 indexed assets still have no bytes.
- S3 still has no recorded visual parent.
- Campaign scope still has no imported rules beyond what a later edit adds.
- Live providers, posting, and image generation are not implemented.
