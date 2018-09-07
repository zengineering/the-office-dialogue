from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    quotes = relationship("OfficeQuote", back_populates="speaker")

    def __repr__(self):
        return "<Character(id={}, name={})>".format(self.id, self.name)


class DialogueLine(Base):
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True)
    line = Column(Text, nullable=False)

    quote = relationship("OfficeQuote", uselist=False, back_populates="line")

    def __repr__(self):
        return "<DialogueLine(id={}, line={})>".format(self.id, self.line)


class OfficeQuote(Base):
    __tablename__ = "office_quotes"

    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    episode = Column(Integer)
    speaker_id = Column(Integer, ForeignKey('characters.id'))
    line_id = Column(Integer, ForeignKey('lines.id'))

    speaker = relationship('Character', uselist=False, back_populates='quotes')
    line = relationship('DialogueLine', uselist=False, back_populates='quote')

    def __repr__(self):
        return ("<OfficeQuote(id={}, season={}, episode={}, speaker_id={}, line_id={})>"
               ).format(self.id, self.season, self.episode, self.speaker_id, self.line_id)


