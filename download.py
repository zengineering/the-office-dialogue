#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup, SoupStrainer, Doctype
from urllib.parse import urljoin
from urllib.error import URLError
from collections import namedtuple
from database import Database, OfficeQuote
from queue import Queue
from threading import Thread
from sys import stderr

Episode = namedtuple("Episode", ['number', 'season', 'scenes'])
Quote = namedtuple("Quote", ['speaker', 'line'])
Scene = namedtuple("Scene", ['quotes', 'deleted'])

def removeDoctypes(soup):
    return filter(lambda t: not isinstance(t, Doctype), soup)

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

    # remove Doctype if nessessary; extract text from each quote block
    scene_texts = [quote_div.text for quote_div in soup]

    # return [ season, episode, [(speaker, spoken)], <deleted scene?> ]
    return (parseScene(st) for st in scene_texts)


def parseScene(scene_text):
    # split on newlines and remove empty items
    scene = list(filter(lambda string: string and not string.isspace(), scene_text.split("\n")))

    # Check if this is a deleted scene; first item is "Deleted Scene <index>"
    deleted = scene[0].rsplit(None, 1)[0].lower() == "deleted scene"

    if deleted:
        scene = scene[1:]

    line_pairs = map(lambda p: Quote(p[0].strip(), p[1].strip()), (line.split(":", 1) for line in scene))

    return Scene(line_pairs, deleted)


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


def fetchPage(url):
    '''
    Request a url and return the contents
    '''
    req = requests.get(url)
    req.raise_for_status()
    return req.content


def extractMatchingUrls(index_url, href):
    # get the index page
    index_content = fetchPage(index_url)
    # extract the a tags with href's matching the re pattern
    a_tags = BeautifulSoup(index_content, "lxml", parse_only=SoupStrainer("a", href=href))
    # filter out Doctype's and extract the urls
    return map(lambda a: a["href"], removeDoctypes(a_tags))


def main():
    root_url = "http://www.officequotes.net/index.php"
    eps_href_re = re.compile("no(\d)-(\d+).php")
    eps_urls = extractMatchingUrls(root_url, eps_href_re)
    print (list(eps_urls))
    return

    episodes = []

    try:
        #episodes = (parseEpisodePage(urljoin(root, link["href"])) for link in eps_links)
        for eps_url in map(lambda a: a["href"], eps_urls):
            match = re.fullmatch(eps_href_re, eps_url["href"])
            if match:
                season, episode = match.groups()
            else:
                raise URLError("Unexpected URL format: {}".format(eps_url["href"]), stderr)
                continue

            url = urljoin(root_url, eps_url["href"])
            scenes = parseEpisodePage(fetchPage(url))
            episodes.append(episode, season, scenes)
            break

    except (URLError, requests.http.HTTPError) as e:
        print("Parsing ({}) failed with error: {}".format(url, e))

main()
