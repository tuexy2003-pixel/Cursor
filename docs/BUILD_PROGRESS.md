# Build progress

## Current phase

Phases 0–5 are in the repository and exercised locally. Phase 6 records providers and assembles a selective context preview. Provider execution returns `NOT_IMPLEMENTED`.

## Completed

- Immutable snapshot at `source_snapshots/2026-10-05/` (111 files, mode `a-w`) with `source_snapshots/2026-10-05.SHA256SUMS`
- `docs/HANDOFF_INGESTION_REPORT.md` and `docs/IMPLEMENTATION_BLUEPRINT.md`
- Alembic revision `76f00d0e35cb_initial_schema` (circular story-lock foreign key added after both tables exist)
- Idempotent handoff importer
- Immutable story-lock versions, approval events, and stale-asset records
- Deterministic validators and regression classifications
- Creative genome facets, account DNA, comment doors, experiments, posts, comments, and mechanic counts
- Operator UI, including a field diff from the previous approved story lock
- Provider stub

## Tests

Local run on this branch:

- `ruff check src tests` passed
- `ruff format --check src tests` passed
- `mypy src` passed
- `pytest`: 10 passed, including a clean Alembic upgrade plus a second import with `inserted=0`
- `apps/web`: `tsc --noEmit` and `next build` passed
- Browser walkthrough: human correction created story-lock v2, kept v1, marked bound assets stale, and showed a `floating_hook` diff. The imported `production-spec-qa` skill still contains “tomorrow”. Benchmarks show `UNKNOWN` where the handoff has no number. A stub run returns `NOT_IMPLEMENTED`.

Clean import counts from `GET /api/summary` before that operator correction:

- programs 1, accounts 3, campaigns 1, creatives 2
- story lock versions 1, skills 15, skill versions 16 (15 skills plus the live-heat query-hygiene playbook)
- policy rules 21, assets 25, regression tests 19, benchmarks 11, source artifacts 111
- importer: `inserted=239 skipped=0`

The running local database also contains the browser verification correction (story lock v2), one experiment, and one stub model run. `creative-os reset-db --seed` restores the imported snapshot only.

## Decisions

- One Python package, `creative_os`
- 9:19.6 is a program preference with absolute ratio tolerance 0.008
- Judgment regression cases return `MODEL_REVIEW_REQUIRED` and never `PASS`
- The transaction math spec’s $5.33 basket is stored only as source prose. The story lock’s $19.23 document is the creative pointer
- The production-spec-qa “tomorrow” example is preserved verbatim in the snapshot and in the imported skill
- SQLite cannot `ALTER` a foreign key, so the current-lock constraint is added with Alembic batch mode after `story_lock_versions` exists

## Known issues

- Example binaries are not in the core snapshot. Asset rows have `present_in_snapshot=false` and no content hash
- Most asset rights are `UNKNOWN`. The operator’s Messages keyboard base is `USER_OWNED`
- Asset relations for parent/base/ingredient chains are not populated, so recursive-edit validation stays `HUMAN_REVIEW_REQUIRED` unless a caller supplies the chain
- No live performance, comment, or experiment history was in the handoff. The experiment and stub run in the local database came from operator verification
- ChatGPT and Grok model versions are `UNKNOWN`
- Phase 6 does not execute providers

## Next work

Import supplemental visual archives when they are available, then attach hashes and rights reviews. Human-approve a new production-spec-qa skill version if the floating-hook example should say “today”. Add real provider adapters only after that policy version exists.
