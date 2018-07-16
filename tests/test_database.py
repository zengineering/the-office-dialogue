import pytest
from tempfile import NamedTemporaryFile
from sqlalchemy import exists

from context import database, dataclasses
from dataclasses import Quote, Episode
from database import *


@pytest.fixture
def db(scope='module'):
    with NamedTemporaryFile() as f:
        setupDbEngine(f.name)
        yield


@pytest.fixture
def session(db):
    with contextSession(commit=True) as session:
        yield session


@pytest.mark.parametrize(('season', 'episode', 'deleted', 'speaker', 'line'),
    (
        (1, 1, False, "Speaker", "Line content"),
    ),
)
def test_addQuote(session, season, episode, deleted, speaker, line):
    quote = OfficeQuote(season=season, episode=episode, deleted=deleted)
    quote.speaker = Character(name=speaker)
    quote.line = DialogueLine(content=line)
    db_add(quote)

    char_q = session.query(Character).filter(Character.name==speaker).all()
    line_q = session.query(DialogueLine).filter(DialogueLine.content==line).all()
    quote_q = session.query(OfficeQuote).filter(
        OfficeQuote.season==season, OfficeQuote.episode==episode,
        OfficeQuote.deleted==deleted).all()

    assert len(char_q) == 1
    assert len(line_q) == 1
    assert len(quote_q) == 1
    assert quote_q[0].speaker.id == char_q[0].id
    assert quote_q[0].line.id == line_q[0].id


