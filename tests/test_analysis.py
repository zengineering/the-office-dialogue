import pytest
from collections import namedtuple
from random import choice

from officequotes.database import *
from officequotes.analysis import getEpisodeCount, getLinesBySeason


@pytest.fixture(scope="module")
def db_content():
    setupDb(":memory:")
    template = "the office {}-{}"
    content = {
        "Dwight": {
            (5,1): [
                "Bears",
                "Beets",
                "Battlestar Galactica",
            ],
            (6,2): [
                "Assitant Regional Manager",
            ],
            (6,3): [
                "Paper"
            ]
        },
        "Michael": {
            (5,1): [
                "Manager",
            ],
            (5,2): [
                "World's best",
                "Boss",
            ],
            (6,4): [
                "Regional Manager",
            ],
            (6,4): [
                "Dunder Mifflin"
            ],
        }
    }

    quotes = []
    for name, dialogue in content.items():
        for (season, episode), lines in dialogue.items():
            for dline in lines:
                quotes.append(
                    OfficeQuote(season=season,
                                episode=episode,
                                speaker=Character(name=name),
                                line=DialogueLine(line=dline)))

    with contextSession(commit=True) as session:
        for quote in quotes:
            session.add(quote)

    yield content


def test_analysis_getEpisodeCount(db_content):
    for name, dialogue in db_content.items():
        assert getEpisodeCount(name) == len(set(dialogue.keys()))


@pytest.mark.parametrize('name', ('Dwight','Michael'))
def test_analysis_getLinesBySeason(db_content, name):
    db_lines = getLinesBySeason(name)
    char_dialogue = db_content[name]

    db_count = sum(len(season) for season in db_lines)
    expected_count = sum(len(episode) for episode in char_dialogue.values())
    assert db_count == expected_count

    season, episode = choice(list(char_dialogue.keys()))
    assert choice(char_dialogue[(season, episode)]) in db_lines[season-1]

