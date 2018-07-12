from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    quote = relationship("OfficeQuote", back_populates="speaker")

    def __repr__(self):
        return "<Character(name={})>".format(self.name)


class DialogueLine(Base):
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    quote = relationship("OfficeQuote", uselist=False, back_populates="line")

    def __repr__(self):
        return "<DialogueLine(content={})>".format(self.content)


class OfficeQuote(Base):
    __tablename__ = "office_quotes"

    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    episode = Column(Integer)
    speaker_id = Column(Integer, ForeignKey('characters.id'))
    line_id = Column(Integer, ForeignKey('lines.id'))
    deleted = Column(Boolean)

    speaker = relationship('Character', uselist=False, back_populates='quote')
    line = relationship('DialogueLine', uselist=False, back_populates='quote')

    def __repr__(self):
        return "<OfficeQuote(season={}, episode={}, speaker_id={}, line_id={}, deleted={})>".format(
            self.season, self.episode, self.speaker_id, self.line_id, self.deleted)


