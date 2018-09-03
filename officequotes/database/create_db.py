import json
from collections import defaultdict
from tqdm import tqdm
from pathlib import Path

from .db_interface import setupDb, engine
from .tables import Character, DialogueLine, OfficeQuote

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

    def items(self):
        return self.__items



def addToDb(episode, speaker_ids, base_line_id):
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
                line = quote['line']
            ) for i, quote in enumerate(episode['quotes'])
        ]
    )



def create_db(db_path, json_dir):
    setupDb(db_path)
    speaker_ids = UniqueValueDict()
    line_id = 1

    json_path_root = Path(json_dir).resolve()
    json_files = list(json_path_root.glob('**/the-office-S*-E*.json'))

    for jf in tqdm(json_files):
        with open(jf) as f:
            eps_dict = json.load(f)
        addToDb(eps_dict, speaker_ids, line_id)

    conn = engine.connect()
    conn.execute(
        Character.__table__.insert(),
        [
            dict(
                id = unique_id,
                name = name
            ) for name, unique_id in speaker_ids.items()
        ]
    )


