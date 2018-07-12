from sqlalchemy import create_engine, Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from os.path import realpath
from contextlib import contextmanager

Base = declarative_base()
Session = sessionmaker()


class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    quote = relationship("OfficeQuote", back_populates="speaker")


class DialogueLine(Base):
    __tablename__ = "lines"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    quote = relationship("OfficeQuote", uselist=False, back_populates="line")


class OfficeQuote(Base):
    __tablename__ = "office_quotes"

    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    episode = Column(Integer)
    speaker_id = Column(Integer, ForeignKey('characters.id'))
    speaker = relationship('Character', uselist=False, back_populates='quote')
    line_id = Column(Integer, ForeignKey('lines.id'))
    line = relationship('DialogueLine', uselist=False, back_populates='quote')
    deleted = Column(Boolean)


    def __repr__(self):
        return "<OfficeQuote(season={}, episode={}, speaker_id={}, line_id={}, deleted={})>".format(
            self.season, self.episode, self.speaker_id, self.line_id, self.deleted)


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

