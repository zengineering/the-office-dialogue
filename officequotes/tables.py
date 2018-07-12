from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


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


