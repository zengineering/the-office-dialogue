import pytest
from tempfile import NamedTemporaryFile
from sqlalchemy import exists, func

from context import database, dataclasses
from dataclasses import Quote, Episode
from database import *


@pytest.fixture
def db(scope='module'):
    with NamedTemporaryFile() as f:
        setupDbEngine("sqlite:///{}".format(f.name))
        yield


def test_db_addQuote(db):
    season, episode, deleted, speaker, line = 1, 1, False, "Speaker", "Line content"
    addQuote(season, episode, deleted, speaker, line)

    with contextSession() as session:
        assert session.query(Character).filter(Character.name==speaker).count() == 1
        assert session.query(DialogueLine).filter(DialogueLine.content==line).count() == 1
        assert session.query(OfficeQuote).filter(
            OfficeQuote.season==season, OfficeQuote.episode==episode).count() == 1

        char = session.query(Character).filter(Character.name==speaker).first()
        quote = session.query(OfficeQuote).filter(
            OfficeQuote.season==season, OfficeQuote.episode==episode).first()
        line = session.query(DialogueLine).filter(DialogueLine.content==line).first()


        assert quote.speaker.id == char.id
        assert quote.speaker.name == char.name
        assert quote.line.id == line.id
        assert quote.deleted == deleted


def test_db_existingSpeaker(db):
    season, episode, deleted, speaker, line = 1, 1, False, "Speaker", "Line content"
    for i in range(2):
        addQuote(season+i, episode+i, deleted, speaker, line)

    with contextSession() as session:
        char_q = session.query(Character).filter(Character.name==speaker).all()
        assert len(char_q) == 1
        assert len(char_q[0].quotes) == 2

        for char_id, in session.query(OfficeQuote.speaker_id).all():
            assert char_id == char_q[0].id


def test_db_addMultiple(db):
    season, episode, deleted, speaker, line = 5, 13, False, "Speaker{}", "Line {}"
    count = 1024
    for i in range(count):
        addQuote(season, episode, deleted, speaker.format(i%100), line.format(i))

    with contextSession() as session:
        assert session.query(Character.id).count() == 100
        assert len(list(session.query(Character.name).distinct())) == 100
        assert session.query(DialogueLine.id).count() == count

        assert all(map(lambda s: s[0] == season, session.query(OfficeQuote.season).all()))
        assert all(map(lambda e: e[0] == episode, session.query(OfficeQuote.episode).all()))

