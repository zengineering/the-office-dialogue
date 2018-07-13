#!/usr/bin/env python3

import requests
import re
import click
from urllib.parse import urljoin
from queue import Queue
from threading import Thread
from sys import stderr
from database import Database, OfficeQuote
from dataclasses import Episode
from parse import extractMatchingUrls, parseEpisode


req_headers = {"User-Agent":
    ("Mozilla/5.0 (X11; CrOS x86_64 10032.86.0) "
     "AppleWebKit/537.36 (KHTML, like Gecko) "
     "Chrome/63.0.3239.140 Safari/537.36")
}
index_url = "http://www.officequotes.net/index.php"
eps_href_re = re.compile("no(\d)-(\d+).php")


def writeToDatabase(db, queue, eps_count):
    '''
    Write <eps_count> episodes in the queue to a database.
    '''
    successful = 0
    while eps_count > 0 or not queue.empty():
        try:
            episode = queue.get()
            if episode:
                db.addEpisode(episode)
                successful += 1
                print("Stored {} episodes successfully;".format(successful), end=" ")
        except Exception as e:
            print("writeToDatabase failed with:\n{}".format(e), file=stderr)
        finally:
            eps_count -= 1
            print("{} episodes remaining".format(eps_count), end=" "*4 + "\r")

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
            quotes = parseEpisode(content)
            return Episode(episode, season, quotes)
        else:
            return None
    except requests.RequestException as e:
        print("Request for {} failed:\n\t{}".format(eps_url, e), file=stderr)
    except Exception as e:
        print("Episode from url {} failed:\n\t{}".format(eps_url, e), file=stderr)


def fetchAndParse(url_q, episode_q, failed_q, eps_href_re, index_url):
    '''
    Pop a url from the url queue
    Download and parse the episode page at that url
    Push the parsed result into the episode queue
    If parsing or downloading fails, put it in the failed queue
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
            total_episodes - url_q.qsize(), url_q.qsize()), end="\r")


@click.command()
@click.option('--thread_count', '-t', default=16, help="Number of downloading threads.")
@click.option('--db_file', default="the-office-quotes.sqlite",
              help="SQLite database to write results to.")
def download(thread_count, db_file):

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
    thread_pool = [
        Thread(target=fetchAndParse, args=(url_q, episode_q, failed_q, eps_href_re, index_url))
        for _ in range(thread_count)
    ]

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

