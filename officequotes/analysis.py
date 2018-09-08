import click
from sqlalchemy import func, desc

from .database import *

#session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command('analyze', context_settings=CONTEXT_SETTINGS)
@click.argument('db_path', type=click.Path(readable=True))
def analyze(db_path):
    setupDb(db_path)
    with contextSession() as session:
        freq = func.count(OfficeQuote.speaker_id).label('freq')
        character_line_counts = (
            session.query(freq, Character.name)
            .join(Character)
            .group_by(OfficeQuote.speaker_id)
            .having(freq > 100)
            .order_by(desc(freq))
            .all()
        )
        for clc in character_line_counts:
            print(clc)

