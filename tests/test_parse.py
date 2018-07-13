import pytest
from bs4 import BeautifulSoup, Doctype

from context import parse
from parse import withoutDoctypes, strainSoup


def test_withoutDoctypes(testSoup):
    assert any(map(lambda t: isinstance(t, Doctype), testSoup))
    filtered_soup = withoutDoctypes(testSoup)
    assert not any(map(lambda t: isinstance(t, Doctype), filtered_soup))


def test_strainSoup(testSoup):
    strainSoup(testSoup)
    for tag in 'biu':
        assert not testSoup(tag)
    assert not testSoup('br')
    assert not testSoup.findAll("div", {"class": "spacer"})


def test_quote_extraction(episodeSoup):
    strainSoup(episodeSoup)
    for tag in withoutDoctypes(episodeSoup):
        assert tag['class'] == ['quote']
