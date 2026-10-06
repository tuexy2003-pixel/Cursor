import argparse
import logging
from collections.abc import Callable
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from creative_os.config import get_settings, repo_root
from creative_os.db import make_engine, make_session_factory, resolve_database_url
from creative_os.importers.examples import import_visual_supplements
from creative_os.importers.handoff import import_handoff
from creative_os.services.baseline import apply_preservation_baseline


def _alembic_config() -> Config:
    settings = get_settings()
    config = Config(str(repo_root() / "alembic.ini"))
    config.set_main_option("script_location", str(repo_root() / "alembic"))
    config.set_main_option("sqlalchemy.url", resolve_database_url(settings.database_url))
    return config


def migrate() -> None:
    settings = get_settings()
    path = settings.sqlite_path()
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
    command.upgrade(_alembic_config(), "head")


def reset_db(seed: bool) -> None:
    settings = get_settings()
    path = settings.sqlite_path()
    if path is not None and path.exists():
        path.unlink()
    migrate()
    if seed:
        seed_baseline()


def import_snapshot() -> None:
    settings = get_settings()
    engine = make_engine()
    factory = make_session_factory(engine)
    session = factory()
    try:
        report = import_handoff(session, settings.resolved_snapshot_root())
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    print(f"inserted={report.inserted} skipped={report.skipped}")
    for note in report.notes:
        print(f"note: {note}")


def supplement_root() -> Path:
    return repo_root() / "source_snapshots/supplements/2026-10-05"


def import_examples() -> None:
    _run_session("examples", lambda session: import_visual_supplements(session, supplement_root()))


def apply_baseline() -> None:
    _run_session("baseline", lambda session: apply_preservation_baseline(session))


def seed_baseline() -> None:
    settings = get_settings()
    engine = make_engine()
    factory = make_session_factory(engine)
    session = factory()
    try:
        report = import_handoff(session, settings.resolved_snapshot_root())
        visual = import_visual_supplements(session, supplement_root())
        baseline = apply_preservation_baseline(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    print(f"inserted={report.inserted} skipped={report.skipped}")
    for note in report.notes:
        print(f"note: {note}")
    print(
        "examples "
        f"a={visual['archive_a_files']} b={visual['archive_b_files']} "
        f"matched={visual['index_matches']} children={visual['child_assets']} "
        f"relations_added={visual['relations']} links_added={visual['example_links']}"
    )
    print(f"baseline policy={baseline['policy']} scope={baseline['scope']}")


def _run_session(label: str, operation: Callable[[Session], object]) -> None:
    engine = make_engine()
    factory = make_session_factory(engine)
    session = factory()
    try:
        result = operation(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    print(f"{label} {result}")


def export_context_bundle(bundle_id: str, export_format: str, output: str | None) -> None:
    import json

    from creative_os.models import ContextBundle
    from creative_os.services.provider_packet import packet_document

    engine = make_engine()
    factory = make_session_factory(engine)
    session = factory()
    try:
        bundle = session.get(ContextBundle, bundle_id)
        if bundle is None:
            raise SystemExit(f"context bundle {bundle_id} was not found")
        if export_format == "markdown":
            text = bundle.compiled_text
        elif export_format == "json":
            text = json.dumps(packet_document(bundle), indent=2, ensure_ascii=False) + "\n"
        else:
            raise SystemExit("format must be markdown or json")
    finally:
        session.close()
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="" if text.endswith("\n") else "\n")


def serve() -> None:
    import uvicorn

    from creative_os.services.deployment import assert_local_operator_deployment

    settings = get_settings()
    assert_local_operator_deployment(settings.api_host)
    uvicorn.run(
        "creative_os.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=get_settings().log_level)
    parser = argparse.ArgumentParser(prog="creative-os")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("migrate", help="Apply database migrations")
    sub.add_parser("import-handoff", help="Idempotently import the snapshot")
    sub.add_parser("import-examples", help="Attach supplemental visual archives")
    sub.add_parser("apply-baseline", help="Apply the working policy and scope corrections")
    reset = sub.add_parser("reset-db", help="Delete the local SQLite database and migrate")
    reset.add_argument("--seed", action="store_true", help="Import the handoff after reset")
    sub.add_parser("serve", help="Run the API")
    export = sub.add_parser("export-context-bundle", help="Export a frozen provider packet")
    export.add_argument("bundle_id")
    export.add_argument("--format", required=True, choices=("markdown", "json"))
    export.add_argument("--output")
    args = parser.parse_args(argv)
    if args.command == "migrate":
        migrate()
    elif args.command == "import-handoff":
        import_snapshot()
    elif args.command == "import-examples":
        import_examples()
    elif args.command == "apply-baseline":
        apply_baseline()
    elif args.command == "reset-db":
        reset_db(seed=args.seed)
    elif args.command == "serve":
        serve()
    elif args.command == "export-context-bundle":
        export_context_bundle(args.bundle_id, args.format, args.output)


if __name__ == "__main__":
    main()
