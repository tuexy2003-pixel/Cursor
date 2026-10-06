import pytest
from sqlalchemy.orm import Session

from creative_os.config import repo_root
from creative_os.db import make_engine, make_session_factory
from creative_os.models import Base


def pytest_collection_modifyitems(config, items) -> None:
    visual = repo_root() / "source_snapshots/supplements/2026-10-05/examples/target_chore_stuff_v6/s1_v6b.png"
    if visual.is_file():
        return
    skip = pytest.mark.skip(reason="supplemental visual binaries are not in this tree")
    for item in items:
        if "full_assets" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def session(tmp_path) -> Session:
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)
    db = factory()
    try:
        yield db
        db.commit()
    finally:
        db.close()
