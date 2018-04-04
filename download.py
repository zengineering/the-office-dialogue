#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup, SoupStrainer, Doctype
import re
from itertools import zip_longest, islice

def grouper(iterable, n, fillvalue=None):
    '''
    Collect data into fixed-length chunks or blocks
    grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    '''
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def peek(gen):
    '''
    look at the next value in a generator but maintain generator state
    '''
    next_value = next(gen)
    return next_value, chain([next_value], gen)

def parseScene(scene_text):
    # split on newlines and remove empty items
    scene = list(filter(lambda string: string and not string.isspace(), scene_text.split("\n")))

    # Check if this is a deleted scene; first item is "Deleted Scene <index>"
    deleted = scene[0].rsplit(None, 1)[0].lower() == "deleted scene"

    if deleted:
        scene = scene[1:]

    line_pairs = map(lambda p: (p[0].strip(), p[1].strip()), (line.split(":", 1) for line in scene))

    return line_pairs, deleted


def parseEpisodePage(url):
    req = requests.get(url)
    req.raise_for_status()

    # parse only <div class="quote"> blocks
    # NOTE: SoupStrainer does not remove Doctype; filter later
    soup = BeautifulSoup(req.content, "lxml", parse_only=SoupStrainer("div", {"class": "quote"}))

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

    # remove Doctype if nessessary; extract text from each quote block
    scene_texts = [quote.text for quote in filter(lambda q: type(q) is not Doctype, soup)]

    # return [ [(speaker, spoken)], <deleted scene?> ]
    return (parseScene(st) for st in scene_texts)



root = "http://www.officequotes.net"
index = "{}/index.php".format(root)

req = requests.get(root)
req.raise_for_status()

eps_link_re = re.compile("no\d-\d+.php")
eps_links = filter(lambda link: hasattr(link, "href"), BeautifulSoup(req.content, "lxml", parse_only=SoupStrainer("a", href=eps_link_re)))

for link in eps_links:
    print(link["href"])
    getEpisodeQuotes("{}/{}".format(root, link["href"]))
    break


#naveps = soup.find_all("div", {"class": "navEp"})[0]
