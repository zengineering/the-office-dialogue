import pytest
from bs4 import BeautifulSoup, Doctype, SoupStrainer
from itertools import tee
from pathlib import Path

from context import test_path
from download.parse import withoutDoctypes, removeTags, parseScene, parseEpisode, extractMatchingUrls
from download.dataclasses import Quote
from download.download import eps_href_re

@pytest.fixture
def testSoup():
    '''
    BeautifulSoup result of parsing test HTML with tags of interest
    '''
    html = (
        '<!DOCTYPE html> <html> '
        '<head> <title>Page Title</title> </head> '
        '<body>'
        '<h1>Heading</h1>'
        '<p>Paragraph</p>'
        '<div class="spacer">&nbsp</div>'
        '<b>Bold</b>'
        '<i>Italics</i>'
        '<u>Underline</u>'
        '<b><i><u>All three</b></i></u>'
        'Some text ending with a linebreak <br />'
        '</body>'
        '</html>'
    )
    return BeautifulSoup(html, "lxml")


@pytest.fixture
def episodeSoup():
    '''
    BeautifulSoup result of parsing http://officequotes.net/no5-13.php
    '''
    html = episodeHtml()
    soup = BeautifulSoup(html, "lxml", parse_only=SoupStrainer("div", {"class": "quote"}))
    removeTags(soup)
    return soup


@pytest.fixture
def episodeHtml():
    '''
    Content of http://officequotes.net/no5-13.php
    '''
    with open(Path(test_path)/'data/no5-13.php', 'rb') as f:
        content = f.read()
    return content


@pytest.fixture
def indexHtml():
    '''
    Content of http://officequotes.net/index.php
    '''
    with open(Path(test_path)/'data/index.php', 'rb') as f:
        content = f.read()
    return content


def test_parse_withoutDoctypes(testSoup):
    assert any(map(lambda t: isinstance(t, Doctype), testSoup))
    filtered_soup = withoutDoctypes(testSoup)
    assert not any(map(lambda t: isinstance(t, Doctype), filtered_soup))


def test_parse_removeTags(testSoup):
    removeTags(testSoup)
    for tag in 'biu':
        assert not testSoup(tag)
    assert not testSoup('br')
    assert not testSoup.findAll("div", {"class": "spacer"})


def test_parse_quote_extraction(episodeSoup):
    for tag in withoutDoctypes(episodeSoup):
        assert tag['class'] == ['quote']


def test_parse_parseScene(episodeSoup):
    scene_text = next(quote_div.text for quote_div in withoutDoctypes(episodeSoup))
    quotes = parseScene(scene_text)

    assert len(quotes) == 1
    assert quotes[0].speaker == "Dwight"
    assert "experience is the best teacher" in quotes[0].line
    assert quotes[0].deleted == False


def test_parse_parseEpisode(episodeHtml):
    quotes = parseEpisode(episodeHtml)

    first = quotes[0]
    assert first.speaker == "Dwight"
    assert "experience is the best teacher" in first.line
    assert first.deleted == False

    last = quotes[-1]
    assert last.speaker == "Michael"
    assert "laughter is the best medicine" in last.line
    assert last.deleted == False


def test_parse_badEpisodeHtml(episodeHtml):
    quotes = parseEpisode(episodeHtml[200:800])
    assert not quotes


def test_parse_extractMatchingUrls(indexHtml):
    '''
    Extract an iterable of URLs matching the given pattern
    '''
    urls = list(extractMatchingUrls(indexHtml, eps_href_re))
    assert len(urls) == 186
    assert "no1-01.php" in urls
    assert "no5-13.php" in urls
    assert "no9-23.php" in urls
