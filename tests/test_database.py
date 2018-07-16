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


def test_db_addQuote(db):
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


#def test_db_addMultiple(db):
#    season, episode, deleted, speaker, line = 5, 13, False, "Speaker", "Line content"
#    for i in range(2):
#        addQuote(season+i, episode+i, deleted, speaker, line)
#
#    with contextSession() as session:
#        char_q = session.query(Character).filter(Character.name==speaker).all()
#        assert len(char_q) == 1
#        assert len(char_q[0].quotes) == 2
#        line_q = session.query(DialogueLine).filter(DialogueLine.content==line).all()
#        assert len(line_q) == 2
#
#        quote_q = session.query(OfficeQuote).all()
#        assert len(quote_q) == 2
#
