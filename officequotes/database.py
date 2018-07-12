from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import realpath
from contextlib import contextmanager
from . import Base


Session = sessionmaker()


class Database():
    def __init__(self, db_file=""):
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

    def addQuote(self, quote):
        """
        Add quote to database
        """
        with self.session_scope() as session:
            session.add(quote) # dialogLine instance

    def addQuotes(self, quotes):
        """
        Add multiple quotes to database
        """
        with self.session_scope() as session:
            for quote in quotes:
                session.add(quote) # dialogLine instance

