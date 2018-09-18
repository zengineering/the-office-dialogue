import click
import json
from sqlalchemy import func, desc, text
from collections import defaultdict, Counter
from textblob import TextBlob
from tqdm import tqdm
from sys import stdin
import os

from .database import (OfficeQuote, Character, DialogueLine,
                       setupDb, contextSession, create_db)


def getEpisodeCount(character_name):
    '''
    Get the number of episodes that a character appears in.
    '''
    with contextSession() as session:
        return (session.query(OfficeQuote.season, OfficeQuote.episode)
                        .join(Character)
                        .filter(Character.name == character_name)
                        .distinct()
                        .count())


def getLinesBySeason(character_name):
    '''
    Get a nested list of lines spoken by the given character in each season.

    Length of the outer list is the number of seasons.
    Length of the inner lists is the number of lines spoken in that season.

    NOTE: Indexing is 0-based, so season_1 lines are at [0], etc
    '''
    with contextSession() as session:
        lines = (session.query(OfficeQuote.season, DialogueLine.line)
                        .filter(Character.name == character_name)
                        .join(Character)
                        .join(DialogueLine)
                        .all())

    lines_by_season = [[] for _ in range(9)]
    for season, line in lines:
        lines_by_season[season-1].append(line)
    return lines_by_season


def analyzeLines(lines_by_season, name=None):
    '''
    Analyze a list of lines on a per-season basis.

    returns: a dict of lists, the values of which are (per-season)
             line count, word count, sentence count, polarity, subjectivity
    '''
    textblobs = [TextBlob(' '.join(season_lines)) for season_lines in lines_by_season]
    word_counts, sentence_counts, polarity, subjectivity = zip(
        *[(len(tb.words), len(tb.sentences), tb.sentiment.polarity, tb.sentiment.subjectivity)
          for tb in tqdm(textblobs, desc=name)])

    return {
        'lines': [len(season_lines) for season_lines in lines_by_season],
        'words': word_counts,
        'sentences': sentence_counts,
        'polarity': polarity,
        'subjectivity': subjectivity
    }


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('db_path', type=click.Path(readable=True, resolve_path=True))
@click.argument('names', nargs=-1, required=False)
@click.option('--output', '-o',
              default=os.getcwd(),
              type=click.Path(writable=True, file_okay=False, resolve_path=True),
              help="Path to directory for output file.")
def analyze_character(db_path, names, output):
    '''
    Analyze all dialogue for a character.

    Analyze on a per-season basis the dialogue of the specified characters.
    Specify names after DB_PATH or via stdin.

    DB_PATH: path to the database
    NAME[S]: name of character to analyze dialogue for.
    OUTPUT: directory in which to store output json.
    '''
    if names:
        character_names = names
    else:
        character_names = [name.strip() for name in stdin.readlines()]

    analyses = {}
    setupDb(db_path)
    for character_name in tqdm(character_names, desc="Analysis"):
        lines = getLinesBySeason(character_name)
        if lines:
            analysis = analyzeLines(lines, name=character_name)
            analysis['episode_count'] = getEpisodeCount(character_name)
            analyses[character_name] = analysis

    with open(os.path.join(output, 'analysis.json'), 'w') as f:
        json.dump(analyses, f, indent=4)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('db_path', type=click.Path(readable=True, resolve_path=True))
@click.option('--min_line_count', '-m', default=100, help="Filter characters with fewer lines.")
def main_characters(db_path, min_line_count):
    '''
    Return a list of main characters.

    Return a list of characters whose total number of lines is above a threshold
    (specified with -m.).
    '''
    setupDb(db_path)
    with contextSession() as session:
        freq = func.count(OfficeQuote.speaker_id).label('freq')
        characters = (
            session.query(Character.name)
            .join(OfficeQuote)
            .group_by(OfficeQuote.speaker_id)
            .having(freq > min_line_count)
            .all()
        )

    # flatten the 1-element tuples and print
    for char in sum(characters, ()):
        print(char)

