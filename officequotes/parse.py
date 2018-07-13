from bs4 import BeautifulSoup, SoupStrainer, Doctype
from dataclasses import Quote
from itertools import chain


def withoutDoctypes(soup):
    '''
    Remove all Doctype from soup
    '''
    return filter(lambda t: not isinstance(t, Doctype), soup)


def extractMatchingUrls(content, pattern):
    '''
    Extract an iterable of URLs matching the given pattern
    '''
    # extract the a tags with href's matching the re pattern
    a_tags = withoutDoctypes(BeautifulSoup(content, "lxml", parse_only=SoupStrainer("a", href=pattern)))
    # filter out Doctype's and extract the urls
    return map(lambda a: a["href"], a_tags)


def strainSoup(soup):
    '''
    Remove undesired html tags from soup
    '''
    # remove font setting (<b>, <i>, <u>) tags
    tags_to_remove = ("b", "i", "u")
    for tag in tags_to_remove:
        for match in soup.findAll(tag):
            match.unwrap()

    # remove all <br/> tags
    for linebreak in soup.findAll("br"):
        linebreak.extract()

    # remove all <div class="spacer">&nbsp</div>
    for spacer in soup.findAll("div", {"class": "spacer"}):
        spacer.decompose()


def parseEpisodePage(content):
    '''
    Return a list of extracted Quotes from an episode page
    '''
    # parse only <div class="quote"> blocks
    soup = BeautifulSoup(content, "lxml", parse_only=SoupStrainer("div", {"class": "quote"}))

    strainSoup(soup)

    # Extract text from each tag (scene)
    # NOTE: filter Doctype because SoupStrainer does not remove them
    scene_texts = [quote_div.text for quote_div in withoutDoctypes(soup)]

    # filter empty qutoe blocks
    return chain.from_iterable(parseScene(st) for st in scene_texts if st.strip())


def parseScene(scene_text):
    '''
    Return a list of extracted Quotes from a scene block
    '''
    # split on newlines and remove empty items
    scene = list(filter(lambda string: string and not string.isspace(), scene_text.split("\n")))

    # Check if this is a deleted scene; first item is "Deleted Scene <index>"
    deleted = scene[0].rsplit(None, 1)[0].lower() == "deleted scene"

    if deleted:
        scene = scene[1:]

    # each line in scene is of the format "Speaker: dialog line"
    # split on ":" (should result in list of len 2), strip any excess whitespace, and store in a Quote
    quotes = []
    for line in scene:
        pair = [s.strip() for s in line.split(":", 1)]
        if len(pair) != 2:
            #print("Skipping line with unexpected format: {}".format(line))
            continue
        quotes.append(Quote(*pair, deleted))

    return quotes
