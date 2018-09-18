import json
import click
import re
from collections import defaultdict
from tqdm import tqdm
from pathlib import Path

from .db_interface import setupDb, getEngine
from .tables import Character, DialogueLine, OfficeQuote

class UniqueValueDict():
    '''
    Wrapper around a defaultdict.
    Default values are based on an autoincrementing counter,
        i.e. at the time of insert, the value is the number of
        previously-inserted values

    '''
    def __init__(self):
        self.__current = 0
        self.__items = defaultdict(self.__next_id)

    def __next_id(self):
        self.__current += 1
        return self.__current

    def __getitem__(self, key):
        return self.__items[key]

    def __setitem__(self, key, value):
        if key not in self.__items:
            self.__items[key] = value

    def __len__(self):
        return len(self.__items)

    def keys(self):
        return self.__items.keys()

    def values(self):
        return self.__items.values()

    def items(self):
        return self.__items.items()


context_regex = re.compile('\[.*?\]')
def removeContext(line):
    '''
    Remove contextual descriptions from dialogue line
    e.g. "[on phone] Hello?"
    '''
    return re.sub(context_regex, '', line)


def addEpisodeToDb(episode, speaker_ids, base_line_id):
    '''
    Add an episode to the database.

    episode: dict of (season, episode number, [list of quotes]
             quote is dict of (speaker/character, line)
    speaker_ids: a UniqueValueDict of character names
    base_line_id: integer offset for primary id's of DialogueLine's
    '''
    engine = getEngine()
    conn = engine.connect()
    conn.execute(
        OfficeQuote.__table__.insert(),
        [
            dict(
                season = episode['season'],
                episode = episode['episode'],
                speaker_id = speaker_ids[quote['speaker']],
                line_id = base_line_id + i
            ) for i, quote in enumerate(episode['quotes'])
        ]
    )
    conn.execute(
        DialogueLine.__table__.insert(),
        [
            dict(
                id = base_line_id + i,
                line = removeContext(quote['line'])
            ) for i, quote in enumerate(episode['quotes'])
        ]
    )


def addCharactersToDb(characters):
    '''
    Add a list of characters to the database.

    characters: {character name: primary id}
    '''
    engine = getEngine()
    conn = engine.connect()
    conn.execute(
        Character.__table__.insert(),
        [
            dict(
                id = unique_id,
                name = name
            ) for name, unique_id in characters.items()
        ]
    )



CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('db_path', '-o',
              default="officequotes.sqlite",
              type=click.Path(writable=True),
              help="Path to output database.")
@click.argument('json_dir', type=click.Path(exists=True))
def create_db(db_path, json_dir):
    '''
    Create database from JSON files.

    Read all JSON files in JSON_DIR and create a sqlite database
    from the data.

    It is recovmmended to run officequotes.corrections before
    creating the database.

    JSON_DIR must be a directory of the same structure as the
    outupt of officequotes.download
    '''
    setupDb(db_path)
    speaker_ids = UniqueValueDict()
    line_id = 1

    # glob the files
    json_path_root = Path(json_dir).resolve()
    json_files = list(json_path_root.glob('**/the-office-S*-E*.json'))

    # read each file and add lines database
    for jf in tqdm(json_files):
        try:
            with open(jf) as f:
                eps_dict = json.load(f)
            addEpisodeToDb(eps_dict, speaker_ids, line_id)
            line_id += len(eps_dict['quotes'])
        except:
            print("Problem with file {}".format(jf))
            raise

    # add all characters to database
    addCharactersToDb(speaker_ids)


