import click
import json
from sqlalchemy import func, desc, text

from .database import *


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command('total_line_counts', context_settings=CONTEXT_SETTINGS)
@click.option('output_json', '-o',
              default="total_line_counts.json",
              type=click.Path(writable=True),
              help="Path to output json file.")
@click.argument('db_path', type=click.Path(readable=True))
def total_line_counts(db_path, output_json):
    '''
    Count the total number of lines by each character.

    Using the datbase created by officequotes.create_db,
    produce a JSON file with each character's name,
    database id, and total number of lines spoken.
    '''
    setupDb(db_path)
    with contextSession() as session:
        freq = func.count(OfficeQuote.speaker_id).label('freq')
        character_line_counts = (
            session.query(OfficeQuote.season,
                          OfficeQuote.episode,
                          OfficeQuote.speaker_id,
                          Character.name,
                          freq)
            .join(Character)
            .group_by(OfficeQuote.speaker_id, OfficeQuote.season, OfficeQuote.episode)
            .all()
        )
    #out_json = [dict(zip(('lines', 'id', 'name'), clc)) for clc in character_line_counts]
    #with open(output_json, 'w') as f:
    #    json.dump(out_json, f, indent=4)
    [print(clc) for clc in character_line_counts]

