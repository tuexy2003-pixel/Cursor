# Build progress

## Current phase

Company control plane v0.4.0. Work orders, the published `NEW_CREATIVE_V1` graph, manual specialist import, approval requests, and a narrow MCP interface sit in front of the existing Creative OS records. OpenClaw is not installed. GeeLark, posting, research, and image execution stay disabled. See `docs/COMPANY_CONTROL_PLANE.md`.

## Completed

- Immutable snapshot at `source_snapshots/2026-10-05/` with checksums, plus supplemental visuals beside it
- Versioned skills, story locks, assets, approvals, genome, DNA, experiments, posts, and comments
- Alembic `76f00d0e35cb` initial schema and `b7c1a9e0d4f2` preservation baseline
- Alembic `c8d4e1a07b33` core integrity: canonical story-lock hash, source snapshots, selective staleness, policy provenance, post/genome/DNA bindings, indexes, and foreign keys
- Alembic `e1f6a2c39d55` trust and context: proposal lifecycle, exact snapshot trees, policy eligibility, context bundles, post campaign binding
- Alembic `f7b2d4e81a90` context fidelity: creative tasks, concept candidates, nullable bundle creative, selected concept
- Alembic `b3d8f1a64c20` creative selection: concept batches, manual evaluations, story-audit records, model-run binding
- Alembic `c5a1e8d42f06` safe execution: run authorizations, provider invocations, and deterministic fingerprint provenance
- Alembic `d8e4c1b27a55` freezes the explicit model for each authorized provider
- Alembic `e7b2a9c14d30` company control plane: work orders, workflow versions, step runs, specialists, evidence, approvals, action authorizations, external execution, and MCP audit
- Dry-run context compiler at `GET /api/creatives/{id}/context-preview`
- Persisted context bundles at `POST /api/creatives/{id}/context-bundles`
- Provider packet export: `creative-os export-context-bundle <bundle_id> --format markdown|json`
- Manual packets in `evaluation/model_transfer_v1/`
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
- No live research, image, posting, or purchasing execution. Text reasoning stays gated.
- Authentication is a loopback guard plus `COS_OPERATOR_IDENTITY`, not a user directory

## Next work

A human can configure one provider and authorize the prepared Maria / DoorDash concept smoke test. Do not run comparison or the Target audit until that single run is reviewed.
