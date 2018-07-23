import json
import click
from pathlib import Path

from officequotes.database import contextSession, setupDbEngine, Character

def correctNamesInDb(name_corrections):
    with contextSession() as session:
        name_and_char = (
            (name, session.query(Character).filter(Character.name == name).one_or_none())
            for name in name_corrections.keys()
        )
        for name, char in name_and_char:
            if char:
                char.name = name_corrections[name]


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('db_file', type=click.Path(exists=True))
def corrections(db_file):
    '''
    Read JSON with character name corrections and update the database accordingly.
    '''
    resources_root = Path(__file__).resolve().parent/"resources"
    with open(resources_root/"name_corrections.json") as f:
        name_corrections = json.load(f)

    setupDbEngine("sqlite:///{}".format(realpath(db_file)))

    correctNamesInDb(name_corrections)
