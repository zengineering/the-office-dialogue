import pytest
from bs4 import BeautifulSoup, Doctype
from itertools import tee

from context import parse, dataclasses
from parse import withoutDoctypes, removeTags, parseScene, parseEpisode, extractMatchingUrls
from dataclasses import Quote
from download import eps_href_re


def test_withoutDoctypes(testSoup):
    assert any(map(lambda t: isinstance(t, Doctype), testSoup))
    filtered_soup = withoutDoctypes(testSoup)
    assert not any(map(lambda t: isinstance(t, Doctype), filtered_soup))


def test_removeTags(testSoup):
    removeTags(testSoup)
    for tag in 'biu':
        assert not testSoup(tag)
    assert not testSoup('br')
    assert not testSoup.findAll("div", {"class": "spacer"})


def test_quote_extraction(episodeSoup):
    for tag in withoutDoctypes(episodeSoup):
        assert tag['class'] == ['quote']


def test_parseScene(episodeSoup):
    scene_text = next(quote_div.text for quote_div in withoutDoctypes(episodeSoup))
    quotes = parseScene(scene_text)

    first = quotes[0]
    assert first.speaker == "Dwight"
    assert "experience is the best teacher" in first.line
    assert first.deleted == False


def test_parseEpisode(episodeHtml):
    quotes = parseEpisode(episodeHtml)

    quote = next(quotes)
    assert quote.speaker == "Dwight"
    assert "experience is the best teacher" in quote.line
    assert quote.deleted == False

    for quote in quotes:
        pass

    assert quote.speaker == "Michael"
    assert "laughter is the best medicine" in quote.line
    assert quote.deleted == False


def test_extractMatchingUrls(indexHtml):
    '''
    Extract an iterable of URLs matching the given pattern
    '''
    urls = list(extractMatchingUrls(indexHtml, eps_href_re))
    assert len(urls) == 186
    assert "no1-01.php" in urls
    assert "no9-23.php" in urls
