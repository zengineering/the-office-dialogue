from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .tables import Base

Session = sessionmaker()
engine = None

@contextmanager
def contextSession(*, commit=False):
    """
    Provide a transactional scope around a series of database operations
    """
    session = Session()
    if commit:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    else:
        yield session
        session.close()


def setupDb(db_path):
    global engine
    engine = create_engine("sqlite:///{}".format(db_path), echo=True)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
