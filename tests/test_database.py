import pytest
from tmpfile import NamedTemporaryFile

from context import database, dataclasses
from dataclasses import Quote, Episode
from database import Database, OfficeQuote, Character, DialogueLine


@pytest.fixture
def db():
    with NamedTemporaryFile() as f:
        yield Database(f.name)


def test_addQuote(db, quote):
    quote = OfficeQuote(season=1, episode=1, deleted=False)
    quote.speaker = Character(name="Speaker")
    quote.line = DialogueLine(content="Line content")

    db.add(quote)



