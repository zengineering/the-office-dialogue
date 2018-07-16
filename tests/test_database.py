import pytest
from tempfile import NamedTemporaryFile
from sqlalchemy import exists

from context import database, dataclasses
from dataclasses import Quote, Episode
from database import *


@pytest.fixture
def db(scope='module'):
    with NamedTemporaryFile() as f:
        setupDbEngine("sqlite:///{}".format(f.name))
        yield


@pytest.fixture
def make_quote():
    def _make_quote(season, episode, deleted, speaker, line):
        return OfficeQuote(
            season=season,
            episode=episode,
            deleted=deleted,
            speaker=Character(name=speaker),
            line=DialogueLine(content=line)
        )
    return _make_quote


def test_db_addQuote(db, make_quote):
    season, episode, deleted, speaker, line = 1, 1, False, "Speaker", "Line content"
    addQuote(season, episode, deleted, speaker, line)

    with contextSession() as session:
        char_q = session.query(Character).filter(Character.name==speaker).all()
        line_q = session.query(DialogueLine).filter(DialogueLine.content==line).all()
        quote_q = session.query(OfficeQuote).filter(
            OfficeQuote.season==season, OfficeQuote.episode==episode).all()

        assert len(char_q) == 1
        assert len(line_q) == 1
        assert len(quote_q) == 1
        assert quote_q[0].speaker.id == char_q[0].id
        assert quote_q[0].speaker.name == char_q[0].name
        assert quote_q[0].line.id == line_q[0].id
        assert quote_q[0].deleted == deleted


def test_db_existingSpeaker(db, make_quote):
    season, episode, deleted, speaker, line = 1, 1, False, "Speaker", "Line content"
    for i in range(2):
        addQuote(season+i, episode+i, deleted, speaker, line)

    with contextSession() as session:
        char_q = session.query(Character).filter(Character.name==speaker).all()
        line_q = session.query(DialogueLine).filter(DialogueLine.content==line).all()
        quote_q = session.query(OfficeQuote).filter(
            OfficeQuote.season==season, OfficeQuote.episode==episode).all()

        assert len(line_q) == 2
        assert len(char_q) == 1
        assert len(char_q[0].quotes) == 2


def test_db_addEpisode(db):
    pass
