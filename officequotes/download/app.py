#!/usr/bin/env python3

import click
import asyncio
import aiohttp
import re
from sys import stderr
from urllib.parse import urljoin

from queue import Queue
from os.path import realpath, isfile
from os import rename

from .fetch import fetchContent
from .parse import extractMatchingUrls, parseEpisode
from .threaded import StoppingThread, fetchAndParse, writeToDatabase, progress
from .constants import index_url, eps_href_re, req_headers
from .dataclasses import Episode
from officequotes.database import setupDbEngine

class OfficeError(Exception):
    pass

async def fetch_content(url, session):
    '''
    Download a single episode page
    '''
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        else:
            print("Request failed for {}".format(url), file=stderr)


# parse an episode page into an Episode
# replace fetchAndParse and episodeFactory
async def fetch_and_parse(eps_url, base_url, eps_url_pattern, session):
    '''
    Fetch the content from an episode page and parse it into an Episode instance.
    '''
    content = await fetch_content(urljoin(base_url, eps_url), session)
    if content:
        try:
            season, eps_num = map(int, re.search(eps_url_pattern, eps_url).groups())
        except AttributeError:
            print("URL does not match expected format: {}".format(eps_url), file=stderr)
        else:
            quotes = await asyncio.coroutine(parseEpisode(content))()
            eps = Episode(eps_num, season, quotes)
            return eps


# download and parse all episode pages into a list of Episodes
async def download_all_episodes(base_url, eps_href_re):

    async with aiohttp.ClientSession(headers=req_headers) as session:
        # get the index page and all episode urls
        index_content = await fetch_content(base_url, session)

        if index_content:
            eps_urls = extractMatchingUrls(index_content, eps_href_re)

            eps_tasks = [
                asyncio.ensure_future(fetch_and_parse(eps_url, base_url, eps_href_re, session))
                for eps_url in eps_urls
            ]

            return await asyncio.gather(*eps_tasks)
        else:
            raise OfficeError("Could not download index page")


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
def download_async():
    loop = asyncio.get_event_loop()
    episodes = loop.run_until_complete(download_all_episodes(index_url, eps_href_re))
    loop.close

    with open("officequotes.csv") as f:
        for episode in episodes:
            for quote in episode.quotes:
                f.write("{season}, {episode}, {speaker}, {line}, {deleted}\n".format(
                    episode.season, episode.number, *(quote.to_tuple)))





@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--thread_count', '-t', default=8, help="Number of downloading threads.")
@click.option('--db_file', default="officequotes.sqlite",
              help="SQLite database to write results to.")
def download(thread_count, db_file):
    '''
    Download all quotes from all episodes of The Office and store in a database.
    '''

    if isfile(db_file):
        rename(db_file, db_file+".bak")

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
    progress_thread = StoppingThread(target=progress, args=(url_q, episode_q), name="progress")

    # consumer thread for writing each episode it receives in a queue to the database
    #db_thread = StoppingThread(target=lambda: writeToDatabase(episode_q, url_q.qsize()),
    #                           name="database")
    db_thread = StoppingThread(target=writeToDatabase, args=(episode_q,), name="database")
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

    progress_thread.join()

    while not episode_q.empty():
        pass
    db_thread.stop()
    db_thread.join()

    if not failed_q.empty():
        print("The following pages failed to download:")
        while not failed_q.empty():
            print(failed_q.get())

