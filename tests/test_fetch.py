import pytest
import requests
from tempfile import NamedTemporaryFile

from officequotes.download.fetch import fetchContent, episodeFactory
from officequotes.download.constants import eps_url_regex


@pytest.fixture
def episode_url():
    return "http://officequotes.net/no5-13.php"


def test_dl_fetchContent(episode_url):
    content = fetchContent(episode_url)
    assert "These muffins taste bad" in content


def test_dl_fetchContent_badurl(episode_url):
    with pytest.raises(requests.exceptions.HTTPError):
        content = fetchContent(episode_url+"bad")


def test_dl_episodeFactory(episode_url):
    episode = episodeFactory(episode_url, eps_url_regex)
    assert episode.season == 5
    assert episode.number == 13
    assert len(episode.quotes) > 100


def test_dl_episodeFactory_badurl():
    episode = episodeFactory("bad_url", eps_url_regex)
    assert episode is None
