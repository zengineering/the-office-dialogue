import pytest
from bs4 import BeautifulSoup


@pytest.fixture
def soup():
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
