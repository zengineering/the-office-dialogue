import pytest
from sqlalchemy import exists, func

from officequotes.database import addQuote, Character, contextSession
from officequotes.database.session_interface import db_add
from officequotes.corrections import correctNamesInJson

@pytest.fixture
def name_corrections():
    return { "old{}".format(i): "new{}".format(i) for i in range(10) }


def test_c_correctSingleName(db, name_corrections):
    db_add(Character(name="old1"))
    with contextSession() as session:
        assert session.query(Character.id).filter_by(name = "old1").scalar() is not None
        assert session.query(Character.id).filter_by(name = "new1").scalar() is None

    correctNamesInDb(name_corrections)
    with contextSession() as session:
        assert session.query(Character.id).filter_by(name = "old1").scalar() is None
        assert session.query(Character.id).filter_by(name = "new1").scalar() is not None


def test_c_correctMultipleName(db, name_corrections):
    for old_name in name_corrections.keys():
        db_add(Character(name=old_name))
    correctNamesInDb(name_corrections)

    with contextSession() as session:
        for old_name, new_name in name_corrections.items():
            assert session.query(Character.id).filter_by(name = old_name).scalar() is None
            assert session.query(Character.id).filter_by(name = new_name).scalar() is not None


def test_c_correctNoName(db, name_corrections):
    db_add(Character(name="random_char"))
    with contextSession() as session:
        assert session.query(Character).count() == 1

    correctNamesInDb(name_corrections)
    with contextSession() as session:
        assert session.query(Character.id).filter_by(name = "random_char").scalar()
        assert session.query(Character).count() == 1



def test_c_correctNameWithQuote(db, quote):
    addQuote(*quote)
    correctNamesInDb({"Speaker": "NewSpeaker"})
    with contextSession() as session:
        assert session.query(Character.id).filter_by(name = "Speaker").scalar() is None
        assert session.query(Character.id).filter_by(name = "NewSpeaker").scalar() is not None
