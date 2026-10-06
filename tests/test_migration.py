import json

import pytest
from sqlalchemy import create_engine, text

from creative_os.cli import import_snapshot, migrate

pytestmark = pytest.mark.core


def test_clean_migrate_and_idempotent_import(tmp_path, monkeypatch, capsys) -> None:
    database = tmp_path / "creative_os.db"
    monkeypatch.setenv("COS_DATABASE_URL", f"sqlite:///{database}")
    migrate()
    import_snapshot()
    first = capsys.readouterr().out
    assert "inserted=" in first
    assert "skipped=" in first
    import_snapshot()
    second = capsys.readouterr().out
    assert "inserted=0" in second

    engine = create_engine(f"sqlite:///{database}")
    with engine.connect() as connection:
        skills = connection.execute(text("select count(*) from skill_artifacts")).scalar_one()
        versions = connection.execute(text("select count(*) from skill_versions")).scalar_one()
        regressions = connection.execute(text("select count(*) from regression_tests")).scalar_one()
        locks = connection.execute(text("select count(*) from story_lock_versions")).scalar_one()
        sources = connection.execute(text("select count(*) from source_artifacts")).scalar_one()
        fk = connection.execute(text("pragma foreign_key_list(creatives)")).fetchall()
        columns = connection.execute(text("pragma table_info(assets)")).fetchall()
        links = connection.execute(
            text("select name from sqlite_master where type='table' and name='example_links'")
        ).scalar_one()
    assert skills == 15
    assert versions == 16
    assert regressions == 19
    assert locks == 1
    assert sources == 111
    assert any(row[2] == "story_lock_versions" for row in fk)
    assert any(row[1] == "size_bytes" for row in columns)
    assert links == "example_links"


def test_upgrade_from_baseline_keeps_existing_rows(tmp_path) -> None:
    from datetime import UTC, datetime

    from alembic import command

    from creative_os.cli import _alembic_config
    from creative_os.services.canonical import document_hash

    database = tmp_path / "upgrade.db"
    url = f"sqlite:///{database}"
    config = _alembic_config()
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "b7c1a9e0d4f2")
    engine = create_engine(url)
    now = datetime.now(UTC).isoformat()
    payload = {
        "title": "Kept",
        "floating_hook": "my birthday is literally today 😭",
        "commerce_relation": "order",
    }
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO programs (id, slug, name, description, created_at) "
                "VALUES ('p1', 'mydashperks', 'MyDashPerks', NULL, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO creatives (id, program_id, account_id, campaign_id, ecosystem_id, slug, name, "
                "status, holdout, current_approved_story_lock_version_id, notes, created_at) "
                "VALUES ('c1', 'p1', NULL, NULL, NULL, 'kept', 'Kept', 'produced', 0, NULL, NULL, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO story_locks (id, creative_id, name, created_at) VALUES ('l1', 'c1', 'Kept', :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO story_lock_versions (id, story_lock_id, version_number, supersedes_version_id, "
                "content_json, content_markdown, content_hash, change_reason, approved_by, source_path, "
                "source_hash, created_at) VALUES ('v1', 'l1', 1, NULL, :payload, 'old', 'hash', "
                "'imported', 'Tyrel', 'lock.md', 'hash', :now)"
            ),
            {"payload": json.dumps(payload), "now": now},
        )
        connection.execute(
            text(
                "INSERT INTO source_artifacts (id, relative_path, sha256, size_bytes, kind, imported_at) "
                "VALUES ('s1', 'README.md', 'abc', 3, 'doc', :now)"
            ),
            {"now": now},
        )
    command.upgrade(config, "head")
    with engine.connect() as connection:
        version = connection.execute(
            text("SELECT document_hash, approval_state, content_json, content_hash FROM story_lock_versions")
        ).one()
        artifact = connection.execute(
            text("SELECT snapshot_id, sha256, relative_path FROM source_artifacts")
        ).one()
        label = connection.execute(text("SELECT label FROM source_snapshots")).scalar_one()
    stored = json.loads(version.content_json) if isinstance(version.content_json, str) else version.content_json
    assert version.document_hash == document_hash(stored)
    assert version.approval_state == "APPROVED"
    assert version.content_hash == "hash"
    assert stored["floating_hook"] == "my birthday is literally today 😭"
    assert artifact.sha256 == "abc"
    assert artifact.relative_path == "README.md"
    assert artifact.snapshot_id is not None
    assert label == "2026-10-05"
