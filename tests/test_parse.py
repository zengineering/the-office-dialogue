import pytest
from bs4 import BeautifulSoup, Doctype

from context import parse


def test_withoutDoctypes(soup):
    assert any(map(lambda t: isinstance(t, Doctype), soup))
    filtered_soup = parse.withoutDoctypes(soup)
    assert not any(map(lambda t: isinstance(t, Doctype), filtered_soup))


def test_strainSoup(soup):
    parse.strainSoup(soup)
    for tag in 'biu':
        assert not soup(tag)
    assert not soup('br')
    assert not soup.findAll("div", {"class": "spacer"})
