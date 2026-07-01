from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from phase01.database.models import get_session_factory
from phase02.shared.config import settings


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session_factory = get_session_factory(settings.database_url)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
