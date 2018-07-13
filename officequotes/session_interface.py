from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import realpath
from contextlib import contextmanager
from tables import Base


Session = sessionmaker()


class SessionInterface():
    def __init__(self, db_file="db.sqlite"):
        # create engine
        self.engine = create_engine("sqlite:///{}".format(realpath(db_file)), echo=False)

        # create schema
        Base.metadata.create_all(self.engine)

        # connect session
        Session.configure(bind=self.engine)


    @staticmethod
    @contextmanager
    def session_scope():
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


    def add(self, entry):
        """
        Add entry to the database
        """
        with self.session_scope() as session:
            session.add(entry)


    def getOrCreate(self, model, **kwargs):
        """
        Get an item from the db if it exists; if not, create it
        """
        with self.session_scope() as session:
            instance = session.query(model).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                instance = model(**kwargs)
                session.add(instance)
                return instance
