#!/usr/bin/env python3

import click
import json
from tqdm import tqdm
from urllib.parse import urljoin
from pathlib import Path
from sys import stderr

from .fetch import fetchContent, episodeFactory
from .parse import extractMatchingUrls
from .constants import index_url, eps_url_regex

class OfficeError(Exception):
    pass

def download_all_episodes(eps_urls, eps_url_regex):
    '''
    download and parse all episode pages into a list of Episodes
    '''
    print("Downloading.")
    episodes = []
    failed = []
    for eps_url in tqdm(eps_urls):
        eps = episodeFactory(eps_url, eps_url_regex)
        if eps:
            episodes.append(eps)
        else:
            failed.append(eps_url)
    return episodes, failed


def write_episodes_json(episodes, root_dir):
    '''
    Write all episodes to JSON files
    '''
    print("Writing to file.")
    for episode in tqdm(episodes):
        eps_file =  "the-office-S{:02}-E{:02}.json".format(episode.season, episode.number)
        with open(root_dir/"season{}".format(episode.season)/eps_file, 'w') as f:
            json.dump(episode.to_dict(), f)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--output_dir', '-o', default="officequotes-json", help="Directory for output json.")
def download(output_dir):
    '''
    Download all quotes from all episodes of The Office and write to csv files.
    '''

    # set up output directory structure
    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    for season in range(1,10):
        (output_root/"season{}".format(season)).mkdir(parents=True, exist_ok=True)

    index_content = fetchContent(index_url)
    if index_content:
        eps_urls = [urljoin(index_url, eps_url)
                    for eps_url in extractMatchingUrls(index_content, eps_url_regex)]

    # download episodes
    episodes, failed = download_all_episodes(eps_urls, eps_url_regex)
    write_episodes_json(episodes, output_root)

    # retry if anything failed
    if failed:
        print("Failed to download/parse {} episodes; retrying...".format(len(failed)))
        episodes, failed = download_all_episodes(failed, eps_url_regex)
        write_episodes_json(episodes, output_root)
        for url in failed:
            print("Failed to download {}".format(url), file=stderr)

