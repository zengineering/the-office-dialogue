import pytest
from tempfile import NamedTemporaryFile
from sqlalchemy import exists, func
from collections import namedtuple

Quote = namedtuple("Quote", ('season', 'episode', 'deleted', 'speaker', 'line'))

from context import database, dataclasses
from database import *


@pytest.fixture
def db(scope='module'):
    with NamedTemporaryFile() as f:
        setupDbEngine("sqlite:///{}".format(f.name))
        yield


@pytest.fixture
def quote():
    return Quote(1, 1, False, "Speaker{}", "Line {}")


def test_db_addQuote(db, quote):
    addQuote(*quote)

    with contextSession() as session:
        assert session.query(Character).filter(Character.name==quote.speaker).count() == 1
        assert session.query(DialogueLine).filter(
            DialogueLine.content==quote.line).count() == 1
        assert session.query(OfficeQuote).filter(
            OfficeQuote.season==quote.season, OfficeQuote.episode==quote.episode
            ).count() == 1

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
        addQuote(quote.season+i, quote.episode+i, quote.deleted, quote.speaker, quote.line)

    with contextSession() as session:
        assert session.query(Character).filter(Character.name==quote.speaker).count() == 1
        char = session.query(Character).filter(Character.name==quote.speaker).first()
        assert session.query(OfficeQuote).filter(OfficeQuote.speaker_id==char.id).count() == 2


def test_db_addEpisode(db, quote):
    count = 1024
    for i in range(count):
        addQuote(quote.season, quote.episode, quote.deleted,
                 quote.speaker.format(i%100), quote.line.format(i))

    with contextSession() as session:
        assert session.query(Character.id).count() == 100
        assert len(list(session.query(Character.name).distinct())) == 100
        assert session.query(DialogueLine.id).count() == count

        assert all(map(lambda s: s[0] == quote.season, session.query(OfficeQuote.season).all()))
        assert all(map(lambda e: e[0] == quote.episode, session.query(OfficeQuote.episode).all()))

