#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup, SoupStrainer, Doctype
import re
from urllib.parse import urljoin, urlsplit
from collections import namedtuple

Episode = namedtuple("Episode", ['number', 'season', 'scenes'])

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
    match = re.fullmatch("\/no(\d)-(\d+).php", urlsplit(url).path)
    if match:
        season, episode = match.groups()
    else:
        raise ValueError("Unexpected URL format: {}".format(url))

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

    # return [ season, episode, [(speaker, spoken)], <deleted scene?> ]
    return Episode(episode, season, (parseScene(st) for st in scene_texts))



root = "http://www.officequotes.net/index.php"

req = requests.get(root)
req.raise_for_status()

eps_link_re = re.compile("no\d-\d+.php")
eps_links = filter(lambda link: hasattr(link, "href"), BeautifulSoup(req.content, "lxml", parse_only=SoupStrainer("a", href=eps_link_re)))

#episodes = (parseEpisodePage(urljoin(root, link["href"])) for link in eps_links)
for link in eps_links:
    print(urljoin(root, link["href"]))
    parseEpisodePage(urljoin(root, link["href"]))
    break

