#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup, SoupStrainer, Doctype
import re
from urllib.parse import urljoin, urlsplit
from urllib.error import URLError
from collections import namedtuple

Episode = namedtuple("Episode", ['number', 'season', 'scenes'])
Quote = namedtuple("Quote", ['speaker', 'line'])
Scene = namedtuple("Scene", ['quotes', 'deleted'])

def parseScene(scene_text):
    # split on newlines and remove empty items
    scene = list(filter(lambda string: string and not string.isspace(), scene_text.split("\n")))

    # Check if this is a deleted scene; first item is "Deleted Scene <index>"
    deleted = scene[0].rsplit(None, 1)[0].lower() == "deleted scene"

    if deleted:
        scene = scene[1:]

    line_pairs = map(lambda p: Quote(p[0].strip(), p[1].strip()), (line.split(":", 1) for line in scene))

    return Scene(line_pairs, deleted)


def parseEpisodePage(url):
    match = re.fullmatch("\/no(\d)-(\d+).php", urlsplit(url).path)
    if match:
        season, episode = match.groups()
    else:
        raise URLError("Unexpected URL format: {}".format(url))

    # request the page
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
    scene_texts = [quote_div.text for quote_div in filter(lambda q: type(q) is not Doctype, soup)]

    # return [ season, episode, [(speaker, spoken)], <deleted scene?> ]
    return Episode(episode, season, (parseScene(st) for st in scene_texts))


def writeToDatabase(episode, db):
    for scene, (quotes, deleted) in enumerate(episode.scenes):
        for speaker, line in quotes:
            db.addQuote(OfficeQuote(
                season=episode.season,
                episode=episode.number,
                scene=scene,
                speaker=speaker,
                line=line,
                deleted=deleted))


def main():
    root = "http://www.officequotes.net/index.php"
    req = requests.get(root)
    req.raise_for_status()

    eps_link_re = re.compile("no\d-\d+.php")
    eps_links = filter(lambda link: hasattr(link, "href"), BeautifulSoup(req.content, "lxml", parse_only=SoupStrainer("a", href=eps_link_re)))

    try:
        #episodes = (parseEpisodePage(urljoin(root, link["href"])) for link in eps_links)
        for link in eps_links:
            url = urljoin(root, link["href"])
            print(url)
            parseEpisodePage(url)
            break
    except (URLError, requests.http.HTTPError) as e:
        print("Parsing ({}) failed with error: {}".format(url, e))


main()
