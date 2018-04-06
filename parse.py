from bs4 import BeautifulSoup, SoupStrainer, Doctype

def removeDoctypes(soup):
    return filter(lambda t: not isinstance(t, Doctype), soup)


def extractMatchingUrls(content, href):
    # extract the a tags with href's matching the re pattern
    a_tags = BeautifulSoup(content, "lxml", parse_only=SoupStrainer("a", href=href))
    # filter out Doctype's and extract the urls
    return map(lambda a: a["href"], removeDoctypes(a_tags))


def parseEpisodePage(content):
    # parse only <div class="quote"> blocks
    # NOTE: filter Doctype because SoupStrainer does not remove them
    soup = removeDoctypes(BeautifulSoup(content, "lxml", parse_only=SoupStrainer("div", {"class": "quote"})))

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

    # extract text from each quote block (scene)
    scene_texts = [quote_div.text for quote_div in soup]

    return (parseScene(st) for st in scene_texts)


def parseScene(scene_text):
    # split on newlines and remove empty items
    scene = list(filter(lambda string: string and not string.isspace(), scene_text.split("\n")))

    # Check if this is a deleted scene; first item is "Deleted Scene <index>"
    deleted = scene[0].rsplit(None, 1)[0].lower() == "deleted scene"

    if deleted:
        scene = scene[1:]

    # each line in scene is of the format "Speaker: dialog line"
    # split on ":" (should result in list of len 2), strip any excess whitespace, and store in a Quote
    line_pairs = map(lambda pair: Quote(*map(lambda s: s.strip(), pair)), (line.split(":", 1) for line in scene))

    return Scene(line_pairs, deleted)
