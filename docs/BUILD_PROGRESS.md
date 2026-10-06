# Build progress

## Current phase

Trust and context bundles v0.2.1. Tags `v0.1.0-preservation-baseline` and `v0.2.0-core-integrity` are unchanged. Provider execution still returns `NOT_IMPLEMENTED`. See `docs/V0_2_1_TRUST_CONTEXT.md`.

## Completed

- Immutable snapshot at `source_snapshots/2026-10-05/` with checksums, plus supplemental visuals beside it
- Versioned skills, story locks, assets, approvals, genome, DNA, experiments, posts, and comments
- Alembic `76f00d0e35cb` initial schema and `b7c1a9e0d4f2` preservation baseline
- Alembic `c8d4e1a07b33` core integrity: canonical story-lock hash, source snapshots, selective staleness, policy provenance, post/genome/DNA bindings, indexes, and foreign keys
- Alembic `e1f6a2c39d55` trust and context: proposal lifecycle, exact snapshot trees, policy eligibility, context bundles, post campaign binding
- Dry-run context compiler at `GET /api/creatives/{id}/context-preview`
- Persisted context bundles at `POST /api/creatives/{id}/context-bundles`
- Portable review marker `pytest -m core`

## Checks

On this branch, after the integrity migration:

- `ruff check`, `ruff format --check`, `mypy`, and `pytest`
- `apps/web`: `tsc --noEmit` and `next build`
- `PYTHONPATH=src pytest -m core` is the command for a source-review zip that keeps the core checksum tree (including the contact-sheet jpg) and omits supplemental visual binaries

## Decisions

- `document_hash` is new. Imported `content_hash` and `source_hash` stay historical.
- Human corrections use the server operator identity. Proposals cannot move the approved pointer.
- Staleness follows declared JSON paths. Bases and ingredients are not stale just because a hook changed.
- 9:19.6 remains a program preference. Hard invariants are not dropped to fit a context budget.
- Remote non-loopback deployment is refused until authentication exists.

## Known issues

- 17 indexed assets still have no binary
- Most rights remain `UNKNOWN`
- S3 has no stated visual parent
- No live performance or provider execution
- Authentication is a loopback guard plus `COS_OPERATOR_IDENTITY`, not a user directory

## Next work

External review of the v0.2 architecture. Do not enable provider execution until that review.
