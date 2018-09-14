import pytest
from tempfile import NamedTemporaryFile
from collections import namedtuple

from officequotes.database import setupDb

#@pytest.fixture
#def db():
#    with NamedTemporaryFile() as f:
#        setupDbEngine("sqlite:///{}".format(f.name))
#        yield


@pytest.fixture
def db():
    setupDb(":memory:")
    yield


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

