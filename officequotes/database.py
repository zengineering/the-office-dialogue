from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import realpath
from contextlib import contextmanager
from tables import Base, Character, DialogueLine, OfficeQuote


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


    def addEpisode(self, episode):
        """
        Convert each quote in an episode into the database schema class
            and write them to the database.
        """
        for quote in episode.quotes:
            db_quote = OfficeQuote(
                season=episode.season,
                episode=episode.number,
                deleted=scene.deleted))
            db_quote.speaker = self.getOrCreate(session, Character, name=quote.speaker)
            db_quote.line = DialogueLine(content=quote.line)

            self.add(quote)


