# v0.2.1 trust, attribution, and context bundles

## Problem

v0.2 left a few trust bugs. Approving a StoryLock proposal moved the current pointer while the row stayed `PENDING`, `approved_by` stayed empty, and affected assets were not marked stale. An existing snapshot label accepted added or deleted files and rewrote `root_hash`. A pending narrower policy could replace an approved global invariant. Context preview listed skill ids without the skill text, and mechanic windows used the clock at compile time.

## Old behavior

`decide_story_lock_version` only moved `Creative.current_approved_story_lock_version_id`. Snapshot import inserted new paths under the same label. Policy resolution kept the most specific active row and ignored approval and effective dates. Posts accepted `campaign_id` and then dropped it. `ExperimentVariant.post_id` competed with `experiment_variant_posts`.

## New behavior

Semantic StoryLock, skill, and policy content stays immutable. Approval, rejection, and needs-changes go through the decision service, which records an `ApprovalEvent`, sets `approval_state` and `approved_by`, runs the same selective staleness path as a human correction, and then moves the pointer. A proposal that does not supersede the current lock returns `OUTDATED_PROPOSAL / REBASE_REQUIRED`. Corrections and proposals accept `expected_current_story_lock_version_id`. A story-lock version id on another creative is rejected.

A snapshot label is an exact tree. Changed, added, or removed paths raise `SnapshotIntegrityError` and leave the stored snapshot alone. A new label creates a new `SourceSnapshot`. The v0.2 migration inserts an empty `2026-10-05` placeholder with no root hash. The first import seals that placeholder. A later import cannot add, remove, or rewrite files under the same label.

A policy enters context only when it is active, approved, and effective at `as_of`. An active approved global invariant is not replaced by a narrower rule with the same code. Two active versions at the same scope fail instead of sorting by id. Heuristics and preferences still use the more specific scope.

`ContextBundle` stores the exact dry-run package, including required skill text, policy and skill version ids, DNA, genome, `as_of`, and the payload hash. It is immutable. `ModelRun.context_bundle_id` is ready for a future run. No provider is called.

Posts persist `campaign_id`, default account and campaign from the creative when those are set, and reject conflicts. A genome must belong to the creative and the selected story lock. Current publishes reject stale deliverables and assets bound to another lock. Historical backfill is explicit. Comment-door mappings require the post's creative and story-lock ids. Revenue amount is `Decimal`. Subtotal checks use unit price times quantity. SQLite timestamps are normalized before `post_age_hours`.

The Target creative stays unassigned. Tests that need an account set one on the fixture creative only.

## Migration

`e1f6a2c39d55` revises `c8d4e1a07b33`. It adds `context_bundles`, `posts.campaign_id`, `model_runs.context_bundle_id`, and drops `experiment_variants.post_id`.

## Tests

`tests/test_trust.py` covers approval lifecycle, selective staleness, outdated proposals, cross-creative versions, snapshot add/remove, policy eligibility, skill immutability, context bundles, post attribution, timezone reload, decimal revenue, and quantity. `PYTHONPATH=src pytest -m core` remains the portable command.

## Operator surface

`POST /api/creatives/{id}/context-bundles` with `stage` and optional `as_of`. `GET /api/creatives/{id}/context-bundles/{bundle_id}` reads it back. The creative page compiles and shows the bundle, including skill text.

## Remaining limitations

- Loopback plus `COS_OPERATOR_IDENTITY` is still the trust boundary.
- There is no automatic rebase of an outdated proposal.
- Performance interpretation has no dedicated skill yet.
- The Target creative still has no account.
- Live providers, posting, and image generation stay unimplemented.
