#!/usr/bin/env python3

import requests
import re
from urllib.parse import urljoin
from queue import Queue
from threading import Thread
from sys import stderr
from database import Database, OfficeQuote
from containers import Episode
from parse import extractMatchingUrls, parseEpisodePage


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



def episodeFactory(eps_url, eps_url_pattern, index_url):
    try:
        season, episode = map(int, re.fullmatch(eps_url_pattern, eps_url["href"]).groups())
        url = urljoin(index_url, eps_url["href"])
        scenes = parseEpisodePage(fetchPage(url))
        return Episode(episode, season, scenes)
    except Exception as e:
        print("Episode from url {} failed with the following error:\n{}".format(eps_url, e), stderr)



def main():
    index_url = "http://www.officequotes.net/index.php"
    eps_href_re = re.compile("no(\d)-(\d+).php")
    # get the index page
    index_content = fetchPage(index_url)
    eps_urls = extractMatchingUrls(index_content, eps_href_re)
    print (list(eps_urls))
    return

    episodes = Queue()
    for eps_url in eps_urls:
        episodes.put(episodeFactory(eps_url, eps_href_re, index_url))
        break

main()
