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
#from HTMLParser import HTMLParseError

req_headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 10032.86.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.140 Safari/537.36"}


def episodeToDatabase(episode, db):
    '''
    Convert each quote in an episode into the database schema class
        and write them to a database.
    '''
    quotes = []
    for scene_index, scene in enumerate(episode.scenes, 1):
        for quote in scene.quotes:
            quotes.append(OfficeQuote(
                season=episode.season,
                episode=episode.number,
                scene=scene_index,
                speaker=quote.speaker,
                line=quote.line,
                deleted=scene.deleted))
    db.addQuotes(quotes)


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
                print("Stored {} episodes successfully;".format(successful), end=" ")
        except Exception as e:
            print("writeToDatabase failed with:\n{}".format(e), file=stderr)
        finally:
            eps_count -= 1
            print("{} episodes remaining".format(eps_count), end="\r")

    return successful


def fetchContent(url):
    '''
    Request a url and return the contents.
    '''
    req = requests.get(url, headers=req_headers)
    req.raise_for_status()
    return req.text


def episodeFactory(eps_url, eps_url_pattern, index_url):
    '''
    Fetch the content from an episode page and convert it to an Episode instance.
    '''
    try:
        season, episode = map(int, re.fullmatch(eps_url_pattern, eps_url).groups())
        url = urljoin(index_url, eps_url)
        content = fetchContent(url)
        if content:
            scenes = parseEpisodePage(content)
            if scenes:
                return Episode(episode, season, scenes)
    except requests.RequestException as e:
        print("Request for {} failed:\n\t{}".format(eps_url, e), file=stderr)
    #except HTMLParseError as e:
    #    print("Parsing for {} failed:\n\t{}".format(eps_url, e), stderr)
    except Exception as e:
        print("Episode from url {} failed:\n\t{}".format(eps_url, e), file=stderr)


def fetchAndParse(url_q, episode_q, failed_q, eps_href_re, index_url):
    '''
    Pop a url from the url queue
    Download and parse the episode page at that url
    Push the parsed result into the episode queue
    '''
    while not url_q.empty():
        eps_url = url_q.get()
        episode = episodeFactory(eps_url, eps_href_re, index_url)
        episode_q.put(episode)
        if episode is None:
            failed_q.put(eps_url)


def downloadProgress(url_q):
    '''
    Show the progress of episode downloads
    '''
    total_episodes = url_q.qsize()
    while not url_q.empty():
        print("Downloaded {} episodes successfully; {} episodes remaining".format(
            total_episodes - url_q.qsize(), total_episodes), end="\r")


def main():
    num_threads = 32
    index_url = "http://www.officequotes.net/index.php"
    db_file = "office-quotes.sqlite"
    eps_href_re = re.compile("no(\d)-(\d+).php")

    # get the index page and all episode urls
    index_content = fetchContent(index_url)
    eps_urls = extractMatchingUrls(index_content, eps_href_re)

    url_q = Queue()
    episode_q = Queue()
    failed_q = Queue()
    database = Database(db_file)

    # queue up all episodes
    for url in eps_urls:
        url_q.put(url)

    # thread to show download progress
    progress_thread = Thread(target=downloadProgress, args=(url_q,), name="progress")

    # consumer thread for writing each episode it receives in a queue to the database
    db_thread = Thread(target=lambda: writeToDatabase(database, episode_q, url_q.qsize()), name="database")

    # producer threads for fetching and parsing episode pages
    thread_pool = [Thread(target=fetchAndParse, args=(url_q, episode_q, failed_q, eps_href_re, index_url)) for _ in range(num_threads)]

    # start the threads
    progress_thread.start()
    db_thread.start()
    for t in thread_pool:
        t.start()

    # join the threads
    for t in thread_pool:
        t.join()
    db_thread.join()
    progress_thread.join()

    if not failed_q.empty():
        print("The following pages failed to download:")
        while not failed_q.empty():
            print(failed_q.get())

main()
