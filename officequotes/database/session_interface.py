from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from .tables import Base


Session = scoped_session(sessionmaker())

class EngineConfig():
    """
    "Singleton" for inititiliazing/updating engine with new db url
    """
    db_url = "officequotes.sqlite"
    engine = None

    @classmethod
    def setupEngine(cls, new_db_url):
        if new_db_url != cls.db_url:
            # create engine
            cls.engine = create_engine(new_db_url, echo=False)

            # create schema
            #Base.metadata.drop_all(engine)
            Base.metadata.create_all(cls.engine)

            # remove current session
            Session.remove()

            # connect session
            Session.configure(bind=cls.engine)

            cls.db_url = new_db_url

setupDbEngine = EngineConfig.setupEngine
engineConnection = lambda: EngineConfig.engine.connect()

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


def db_add(entry):
    """
    Add entry to the database
    """
    with contextSession(commit=True) as session:
        session.add(entry)


def db_getOrCreate(model, **kwargs):
    """
    Get an item from the db if it exists; if not, create it
    """
    with contextSession() as session:
        instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        with contextSession(commit=True) as session:
            instance = model(**kwargs)
            session.add(instance)
    return instance

