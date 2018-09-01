import asyncio
import aiohttp
import pytest

from officequotes.download.app import fetch_content
from officequotes.download.constants import req_headers

@pytest.fixture
async def aioh_session():
    async with aiohttp.ClientSession(headers=req_headers) as session:
        yield session


@pytest.fixture
def episode_url():
    return "http://officequotes.net/no5-13.php"


@pytest.mark.asyncio
async def test_async_fetch_content(episode_url, aioh_session):
    content = await fetch_content(episode_url, aioh_session)
    assert b"These muffins taste bad" in content

