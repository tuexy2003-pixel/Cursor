from creative_os.config import repo_root


def test_snapshot_checksums_match() -> None:
    root = repo_root() / "source_snapshots/2026-10-05"
    sums = (repo_root() / "source_snapshots/2026-10-05.SHA256SUMS").read_text(encoding="utf-8")
    import hashlib

    for line in sums.splitlines():
        digest, relative = line.split("  ", 1)
        data = (root / relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest


def test_snapshot_is_not_writable() -> None:
    path = repo_root() / "source_snapshots/2026-10-05/README.md"
    with pytest_raises_permission():
        path.open("a").write("x")


def test_production_spec_keeps_superseded_hook_example() -> None:
    text = (repo_root() / "source_snapshots/2026-10-05/skills/production-spec-qa/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "my birthday is literally tomorrow" in text
    lock = (
        repo_root() / "source_snapshots/2026-10-05/story_locks/TARGET_chore_stuff_STORY_LOCK_current.md"
    ).read_text(encoding="utf-8")
    assert "my birthday is literally today" in lock


def pytest_raises_permission() -> object:
    import pytest

    return pytest.raises(PermissionError)
