import json
import click
from collections import defaultdict
from tqdm import tqdm
from pathlib import Path

from .db_interface import setupDb, getEngine
from .tables import Character, DialogueLine, OfficeQuote
from .clean import removeContext

class UniqueValueDict():
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



def addEpisodeToDb(episode, speaker_ids, base_line_id):
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
@click.command('create_db', context_settings=CONTEXT_SETTINGS)
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

    json_path_root = Path(json_dir).resolve()
    json_files = list(json_path_root.glob('**/the-office-S*-E*.json'))

    for jf in tqdm(json_files):
        try:
            with open(jf) as f:
                eps_dict = json.load(f)
            addEpisodeToDb(eps_dict, speaker_ids, line_id)
            line_id += len(eps_dict['quotes'])
        except:
            print("Problem with file {}".format(jf))
            raise

    addCharactersToDb(speaker_ids)


