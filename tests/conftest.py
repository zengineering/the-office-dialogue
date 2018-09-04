import pytest
from tempfile import NamedTemporaryFile
from collections import namedtuple

from officequotes.database import setupDbEngine
from officequotes.database.db_interface import setupDb

#@pytest.fixture
#def db():
#    with NamedTemporaryFile() as f:
#        setupDbEngine("sqlite:///{}".format(f.name))
#        yield


@pytest.fixture
def db():
    setupDb(":memory:")
    yield 1


@pytest.fixture
def episode_dict():
    return {
        'season': 5,
        'episode': 13,
        'quotes': [
            {
                "speaker": "Dwight",
                "line": "A lot of ideas were not appreciated in their time."
            },
            {
                "speaker": "Michael",
                "line": "Electricity."
            },
            {
                "speaker": "Dwight",
                "line": "Shampoo."
            }
        ]
    }


Quote = namedtuple("Quote", ('season', 'episode', 'speaker', 'line', 'deleted'))

@pytest.fixture
def fmt_quote():
    return Quote(1, 1, "Speaker{}", "Line {}", False)

@pytest.fixture
def quote():
    return Quote(1, 1, "Speaker", "Line", False)
