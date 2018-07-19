import pytest
from tempfile import NamedTemporaryFile

from context import download
from download.threaded import writeEpisodeToDb
from download.dataclasses import Episode, Quote
from database import contextSession, Character, DialogueLine, OfficeQuote


@pytest.fixture
def episode():
    return Episode(5, 13, [
        Quote("Dwight", "A lot of ideas were not appreciated in their time.", False),
        Quote("Michael", "Electricity.", False),
        Quote("Dwight", "Shampoo.", False)
    ])

def test_dlapp_writeEpisodeToDb(db, episode):
    writeEpisodeToDb(episode)
    with contextSession() as session:
        assert session.query(Character.id).count() == 2
        assert session.query(DialogueLine.id).count() == 3
        char_id = session.query(Character.id).filter(Character.name == "Dwight")
        assert session.query(OfficeQuote.id).filter(OfficeQuote.speaker_id == char_id).count() == 2

