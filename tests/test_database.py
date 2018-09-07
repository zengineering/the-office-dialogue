import pytest

from officequotes.database import *


def test_db_UniqueValueDict():
    uvd = UniqueValueDict()
    keys = ('a', 'b', 'c', 'b', 'a', 'd')
    [uvd[k] for k in keys]
    for val, key in enumerate(('a', 'b', 'c', 'd'), 1):
        assert val == uvd[key]


def test_db_addEpisodeToDb(db, episode_dict):
    speaker_ids = UniqueValueDict()
    base_line_id = 10
    addEpisodeToDb(episode_dict, speaker_ids, base_line_id)
    with contextSession() as session:
        assert session.query(OfficeQuote).count() == 3
        assert all(map(lambda q: q.season == 5 and q.episode == 13,
                       session.query(OfficeQuote)))
        assert session.query(OfficeQuote).filter(
            OfficeQuote.speaker_id == 1).count() == 2
        assert session.query(OfficeQuote).filter(
            OfficeQuote.speaker_id == 2).count() == 1
        for i, line in enumerate(session.query(DialogueLine).order_by(DialogueLine.id)):
            assert line.line == episode_dict['quotes'][i]['line']


def test_db_addCharactersToDb(db):
    speaker_ids = UniqueValueDict()
    char_names = ("Michael", "Dwight", "Jim", "Pam", "Michael")
    ids = [speaker_ids[cn] for cn in char_names]

    addCharactersToDb(speaker_ids)
    with contextSession() as session:
        assert session.query(Character.id).count() == 4
        for char_id, char_name in zip(ids, char_names):
            assert session.query(Character).filter(Character.id == char_id).one().name == char_name

