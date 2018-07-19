import pytest
from tempfile import NamedTemporaryFile
from sqlalchemy import exists, func
from collections import namedtuple

Quote = namedtuple("Quote", ('season', 'episode', 'speaker', 'line', 'deleted'))

from context import database, download
from database import (contextSession, setupDbEngine, addQuote, getCharacter,
                      Character, OfficeQuote, DialogueLine)


@pytest.fixture
def db():
    with NamedTemporaryFile() as f:
        setupDbEngine("sqlite:///{}".format(f.name))
        yield


@pytest.fixture
def quote():
    return Quote(1, 1, "Speaker{}", "Line {}", False)


def test_db_addQuote(db, quote):
    addQuote(*quote)
    with contextSession() as session:
        assert session.query(Character).filter(Character.name==quote.speaker).count() == 1
        assert session.query(DialogueLine).filter(
            DialogueLine.content==quote.line).count() == 1
        assert session.query(OfficeQuote).filter(
            OfficeQuote.season==quote.season, OfficeQuote.episode==quote.episode
            ).count() == 1


def test_db_relationship(db, quote):
    addQuote(*quote)
    with contextSession() as session:
        char = session.query(Character).filter(Character.name==quote.speaker).first()
        officequote = session.query(OfficeQuote).filter(
            OfficeQuote.season==quote.season, OfficeQuote.episode==quote.episode).first()
        line = session.query(DialogueLine).filter(DialogueLine.content==quote.line).first()

        assert officequote.speaker.id == char.id
        assert officequote.speaker.name == char.name
        assert officequote.line.id == line.id
        assert officequote.deleted == quote.deleted


def test_db_existingSpeaker(db, quote):
    for i in range(2):
        addQuote(quote.season+i, quote.episode+i, quote.speaker, quote.line, quote.deleted)

    with contextSession() as session:
        assert session.query(Character).filter(Character.name==quote.speaker).count() == 1
        char = session.query(Character).filter(Character.name==quote.speaker).first()
        assert session.query(OfficeQuote).filter(OfficeQuote.speaker_id==char.id).count() == 2


def test_db_addEpisode(db, quote):
    quote_count = 1024
    speaker_count = 100
    for i in range(quote_count):
        addQuote(quote.season, quote.episode, quote.speaker.format(i % speaker_count),
                 quote.line.format(i), quote.deleted)

    with contextSession() as session:
        assert session.query(Character.id).count() == speaker_count
        assert len(list(session.query(Character.name).distinct())) == speaker_count
        assert session.query(DialogueLine.id).count() == quote_count
        assert all(map(lambda s: s[0] == quote.season, session.query(OfficeQuote.season).all()))
        assert all(map(lambda e: e[0] == quote.episode, session.query(OfficeQuote.episode).all()))


def test_db_getCharacter(db, quote):
    addQuote(*quote)
    assert getCharacter(name=quote.speaker) is not None

