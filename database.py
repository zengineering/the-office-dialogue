from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()

class DialogueLine(Base):
    __tablename__ = "dialogue"

    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    episode = Column(Integer)
    scene = Column(Integer)
    speaker = Column(String)
    line = Column(String)
    deleted = Column(Boolean)

    def __repr__(self):
        return "<DialogueLine(season={}, episode={}, scene={}, speaker={}, line={}, deleted={}".format(
            self.season, self.episode, self.scene, self.speaker, self.line, self.deleted) 



class Database():
    def __init__(self, db_loc="/:memory"):
        # create engine
        self.engine = create_engine("sqlite://{}".format(db_loc), echo=True)

        # create schema
        Base.metadata.create_all(self.engine)

        # connect session
        Session.configure(bind=self.engine)

        self.session = Session()

    def addDialogueLine(self, dialogueLine):
        self.session.add(dialogueLine) # DialogueLine instance
