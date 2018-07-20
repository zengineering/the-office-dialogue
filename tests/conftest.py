import pytest
from tempfile import NamedTemporaryFile

from officequotes.database import setupDbEngine

@pytest.fixture
def db():
    with NamedTemporaryFile() as f:
        setupDbEngine("sqlite:///{}".format(f.name))
        yield
