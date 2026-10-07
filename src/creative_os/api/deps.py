from collections.abc import Iterator

from sqlalchemy.orm import Session

from creative_os.db import make_engine, make_session_factory


def get_session() -> Iterator[Session]:
    factory = make_session_factory(make_engine())
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
