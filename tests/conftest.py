import pytest
from sqlalchemy.orm import Session

from creative_os.db import make_engine, make_session_factory
from creative_os.models import Base


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
