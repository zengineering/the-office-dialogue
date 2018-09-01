import asyncio
import aiohttp
import pytest

from context import test_path
from officequotes.download.app import fetch_content, fetch_and_parse
from officequotes.download.constants import req_headers, eps_href_re
from officequotes.download.dataclasses import Episode

@pytest.fixture
async def aioh_session():
    async with aiohttp.ClientSession(headers=req_headers) as session:
        yield session


@pytest.fixture
def episode_url():
    return "http://officequotes.net/no5-13.php"


def episodeHtml():
    '''
    Content of http://officequotes.net/no5-13.php
    '''
    with open(Path(test_path)/'data/no5-13.php', 'rb') as f:
        content = f.read()
    return content


@pytest.mark.asyncio
async def test_async_fetch_content(episode_url, aioh_session):
    content = await fetch_content(episode_url, aioh_session)
    assert b"These muffins taste bad" in content


@pytest.mark.asyncio
async def test_async_fetch_and_parse(aioh_session, episode_url):
    episode = await fetch_and_parse(episode_url, eps_href_re, aioh_session)
    assert isinstance(episode, Episode)
    assert episode.season == 5
    assert episode.number == 13
    assert len(episode.quotes) > 100
