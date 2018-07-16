from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import realpath
from contextlib import contextmanager
from .tables import Base


Session = sessionmaker()

class EngineConfig():
    db_path = "officequotes.sqlite"

    @classmethod
    def setupEngine(cls, new_db_path):
        if new_db_path != cls.db_path:
            # create engine
            engine = create_engine("sqlite:///{}".format(realpath(new_db_path)), echo=False)

            # create schema
            Base.metadata.create_all(engine)

            # connect session
            Session.configure(bind=engine)

            cls.db_path = new_db_path

setupEngine = EngineConfig.setupEngine

@contextmanager
def sessionScope():
    """
    Provide a transactional scope around a series of operations.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def db_add(entry):
    """
    Add entry to the database
    """
    with sessionScope() as session:
        session.add(entry)


def db_getOrCreate(model, **kwargs):
    """
    Get an item from the db if it exists; if not, create it
    """
    with sessionScope() as session:
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            session.add(instance)
            return instance

