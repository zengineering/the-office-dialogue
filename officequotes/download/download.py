#!/usr/bin/env python3

import requests
import re
import click
from urllib.parse import urljoin
from queue import Queue
from threading import Thread
from sys import stderr
from os.path import realpath

from database import setupDbEngine
from .dataclasses import Episode
from .parse import extractMatchingUrls, parseEpisode
from .fetch import fetchContent, fetchAndParse
from .db_interface import writeToDatabase

req_headers = {"User-Agent":
    ("Mozilla/5.0 (X11; CrOS x86_64 10032.86.0) "
     "AppleWebKit/537.36 (KHTML, like Gecko) "
     "Chrome/63.0.3239.140 Safari/537.36")
}
index_url = "http://www.officequotes.net/index.php"
eps_href_re = re.compile("no(\d)-(\d+).php")

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
    setupDbEngine("sqlite:///{}".format(realpath(db_file)))

    # queue up all episodes
    for url in eps_urls:
        url_q.put(url)

    # thread to show download progress
    progress_thread = Thread(target=downloadProgress, args=(url_q,), name="progress")

    # consumer thread for writing each episode it receives in a queue to the database
    db_thread = Thread(target=lambda: writeToDatabase(episode_q, url_q.qsize()), name="database")

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

