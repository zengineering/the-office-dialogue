import pytest
from tempfile import NamedTemporaryFile
from collections import namedtuple

from officequotes.database import setupDbEngine

@pytest.fixture
def db():
    with NamedTemporaryFile() as f:
        setupDbEngine("sqlite:///{}".format(f.name))
        yield


Quote = namedtuple("Quote", ('season', 'episode', 'speaker', 'line', 'deleted'))

@pytest.fixture
def fmt_quote():
    return Quote(1, 1, "Speaker{}", "Line {}", False)

@pytest.fixture
def quote():
    return Quote(1, 1, "Speaker", "Line", False)
