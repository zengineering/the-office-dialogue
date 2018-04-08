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
from functools import partial

req_headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 10032.86.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.140 Safari/537.36"}


def episodeToDatabase(episode, db):
    '''
    Convert each quote in an episode into the database schema class
        and write them to a database.
    '''
    for scene_index, scene in enumerate(episode.scenes, 1):
        for quote in scene.quotes:
            db.addQuote(OfficeQuote(
                season=episode.season,
                episode=episode.number,
                scene=scene_index,
                speaker=quote.speaker,
                line=quote.line,
                deleted=scene.deleted))


def writeToDatabase(db, queue, eps_count):
    '''
    Write <eps_count> episodes in the queue to a database.
    '''
    successful = 0
    while eps_count > 0 or not queue.empty():
        try:
            episode = queue.get()
            if episode:
                episodeToDatabase(episode, db)
                successful += 1
        except Exception as e:
            print("writeToDatabase failed with:\n{}".format(e))
        finally:
            eps_count -= 1
    return successful


def fetchContent(url):
    '''
    Request a url and return the contents.
    '''
    req = requests.get(url, headers=req_headers)
    req.raise_for_status()
    return req.content


def episodeFactory(eps_url, eps_url_pattern, index_url):
    '''
    Fetch the content from an episode page and convert it to an Episode instance.
    '''
    try:
        season, episode = map(int, re.fullmatch(eps_url_pattern, eps_url).groups())
        url = urljoin(index_url, eps_url)
        scenes = parseEpisodePage(fetchContent(url))
        return Episode(episode, season, scenes)
    except Exception as e:
        print("Episode from url {} failed with the following error:\n{}".format(eps_url, e), stderr)


def main():
    index_url = "http://www.officequotes.net/index.php"
    db_file = "office-quotes.sqlite"
    eps_href_re = re.compile("no(\d)-(\d+).php")

    # get the index page and all episode urls
    index_content = fetchContent(index_url)
    eps_urls = list(extractMatchingUrls(index_content, eps_href_re))

    episodes_q = Queue()
    database = Database(db_file)

    # consumer thread for writing each episode it receives in a queue to the database
    db_thread = Thread(target=lambda: writeToDatabase(database, episodes_q, len(eps_urls)), name="database")

    # producer threads for fetching episode pages, converting to episode objects and pushing in the queue
    eps_thread_func = lambda eps_url: episodes_q.put(episodeFactory(eps_url, eps_href_re, index_url))
    threads = [Thread(target=eps_thread_func, name=eps_url, args=(eps_url,)) for eps_url in eps_urls]

    # start the threads
    db_thread.start()
    for t in threads:
        t.start()

    # join the threads
    for t in threads:
        t.join()
    db_thread.join()


main()
