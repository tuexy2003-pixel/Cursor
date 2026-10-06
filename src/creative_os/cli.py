import argparse
import logging

from alembic import command
from alembic.config import Config

from creative_os.config import get_settings, repo_root
from creative_os.db import make_engine, make_session_factory, resolve_database_url
from creative_os.importers.handoff import import_handoff


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
        import_snapshot()


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


def serve() -> None:
    import uvicorn

    settings = get_settings()
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
    reset = sub.add_parser("reset-db", help="Delete the local SQLite database and migrate")
    reset.add_argument("--seed", action="store_true", help="Import the handoff after reset")
    sub.add_parser("serve", help="Run the API")
    args = parser.parse_args(argv)
    if args.command == "migrate":
        migrate()
    elif args.command == "import-handoff":
        import_snapshot()
    elif args.command == "reset-db":
        reset_db(seed=args.seed)
    elif args.command == "serve":
        serve()


if __name__ == "__main__":
    main()
