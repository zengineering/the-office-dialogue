import pytest
from tempfile import NamedTemporaryFile

from context import database
from database import setupDbEngine

@pytest.fixture
def db():
    with NamedTemporaryFile() as f:
        setupDbEngine("sqlite:///{}".format(f.name))
        yield
