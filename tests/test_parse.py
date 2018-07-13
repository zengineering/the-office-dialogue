import pytest
from bs4 import BeautifulSoup, Doctype

from context import parse


def test_withoutDoctypes():
    html = (
        "<!DOCTYPE html> <html> "
        "<head> <title>Page Title</title> </head> "
        "<body>"
        "<h1>Heading</h1>"
        "<p>Paragraph</p>"
        "</body>"
        "</html>"
    )
    soup = BeautifulSoup(html, "lxml")
    assert any(map(lambda t: isinstance(t, Doctype), soup))
    filtered_soup = parse.withoutDoctypes(soup)
    assert not any(map(lambda t: isinstance(t, Doctype), filtered_soup))
