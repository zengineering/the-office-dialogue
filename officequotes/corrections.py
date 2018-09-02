import json
import click
import os
from pathlib import Path
from tqdm import tqdm

def correctNamesInJson(name_corrections, json_files):
    for jf in tqdm(json_files):
        with open(jf, 'r+') as f:
            episode = json.load(f)
            for quote in tqdm(episode['quotes']):
                quote['speaker'] = name_corrections.get(quote['speaker'], quote['speaker'])
            f.seek(0)
            json.dump(episode, f)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('json_dir', type=click.Path(exists=True))
def corrections(json_dir):
    '''
    Read JSON with character name corrections and update the database accordingly.
    '''
    resources_root = Path(__file__).resolve().parent/"resources"
    with open(resources_root/"name_corrections.json") as f:
        name_corrections = json.load(f)

    dir_tree = os.walk(os.path.realpath(json_dir))
    next(dir_tree) # skip the top
    json_files = []
    for season, _, episodes in dir_tree:
        json_files.extend(os.path.join(season, episode) for episode in episodes)

    correctNamesInJson(name_corrections, json_files)
