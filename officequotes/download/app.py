#!/usr/bin/env python3

import re
import click
from queue import Queue
from os.path import realpath

from .fetch import fetchContent
from .parse import extractMatchingUrls
from .threaded import StoppingThread, fetchAndParse, writeToDatabase, downloadProgress
from .constants import index_url, eps_href_re
from database import setupDbEngine


@click.command()
@click.option('--thread_count', '-t', default=16, help="Number of downloading threads.")
@click.option('--db_file', default="officequotes.sqlite",
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
    progress_thread = StoppingThread(target=downloadProgress, args=(url_q,), name="progress")

    # consumer thread for writing each episode it receives in a queue to the database
    #db_thread = StoppingThread(target=lambda: writeToDatabase(episode_q, url_q.qsize()),
    #                           name="database")
    db_thread = StoppingThread(target=writeToDatabase, args=(episode_q, url_q.qsize()),
                               name="database")
    # producer threads for fetching and parsing episode pages
    thread_pool = [
        StoppingThread(target=fetchAndParse,
                       args=(url_q, episode_q, failed_q, eps_href_re, index_url))
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
    db_thread.stop()
    db_thread.join()
    progress_thread.join()

    if not failed_q.empty():
        print("The following pages failed to download:")
        while not failed_q.empty():
            print(failed_q.get())

