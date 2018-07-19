import pytest
from threading import current_thread
from time import sleep
from queue import Queue

from context import download
from download.download import eps_href_re
from download.threaded import writeEpisodeToDb, StoppingThread, fetchAndParse
from download.dataclasses import Episode, Quote
from database import contextSession, Character, DialogueLine, OfficeQuote


@pytest.fixture
def episode():
    return Episode(5, 13, [
        Quote("Dwight", "A lot of ideas were not appreciated in their time.", False),
        Quote("Michael", "Electricity.", False),
        Quote("Dwight", "Shampoo.", False),
        Quote("Michael", "Other things.", True)
    ])


def test_dlapp_writeEpisodeToDb(db, episode):
    writeEpisodeToDb(episode)
    with contextSession() as session:
        assert session.query(Character.id).count() == 2
        assert session.query(DialogueLine.id).count() == 4
        char_id = session.query(Character.id).filter(Character.name == "Dwight")
        assert session.query(OfficeQuote.id).filter(OfficeQuote.speaker_id == char_id).count() == 2


def test_dlapp_stoppingThread():
    def loop():
        while not current_thread().stopped():
            pass
    t = StoppingThread(target=loop)
    t.start()
    sleep(1)
    t.stop()
    t.join()
    assert 1


def test_dlapp_fetchAndParse():
    url_q = Queue()
    eps_q = Queue()
    fail_q = Queue()
    index_url = "http://officequotes.net"
    for url in ("5-13", "6-04"):
        url_q.put("no{}.php".format(url))

    # producer threads for fetching and parsing episode pages
    t = StoppingThread(target=fetchAndParse, args=(url_q, eps_q, fail_q, eps_href_re, index_url))
    t.start()
    t.join()
    assert url_q.empty()
    assert fail_q.empty()
    assert eps_q.qsize() == 2
    while not eps_q.empty():
        episode = eps_q.get()
        assert isinstance(episode, Episode)
        assert episode.season in (5,6)
        assert episode.number in (4,13)
        assert len(episode.quotes) > 100


