from sqlalchemy import create_engine, Column, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os.path import realpath
from contextlib import contextmanager

Base = declarative_base()
Session = sessionmaker()

class OfficeQuote(Base):
    __tablename__ = "office_quotes"

    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    episode = Column(Integer)
    scene = Column(Integer)
    speaker = Column(Text)
    line = Column(Text)
    deleted = Column(Boolean)

    def __repr__(self):
        return "<OfficeQuote(season={}, episode={}, scene={}, speaker={}, line={}, deleted={})>".format(
            self.season, self.episode, self.scene, self.speaker, self.line, self.deleted) 


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

