import pytest
from bs4 import BeautifulSoup, SoupStrainer
from pathlib import Path

from context import test_path

@pytest.fixture
def testSoup():
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
    with open(Path(test_path)/'data/no5-13.php', 'rb') as f:
        soup = BeautifulSoup(f, "lxml", parse_only=SoupStrainer("div", {"class": "quote"}))

    return soup
