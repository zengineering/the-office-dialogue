import pytest
from tempfile import NamedTemporaryFile

from context import download
from download.fetch import fetchContent, episodeFactory
from download.download import eps_href_re


@pytest.fixture
def episode_url():
    return "http://officequotes.net/no5-13.php"


@pytest.fixture
def req_text(episode_url):
    return fetchContent(episode_url)


def test_dl_fetchContent(episode_url):
    content = fetchContent(episode_url)
    assert "These muffins taste bad" in content


def test_dl_episodeFactory(episode_url):
    episode = episodeFactory(episode_url, eps_href_re)
    assert episode.season == 5
    assert episode.number == 13
    assert len(episode.quotes) > 100
