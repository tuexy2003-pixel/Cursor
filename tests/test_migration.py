from sqlalchemy import create_engine, text

from creative_os.cli import import_snapshot, migrate


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
