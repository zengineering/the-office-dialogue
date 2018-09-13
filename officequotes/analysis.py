import click
import json
from sqlalchemy import func, desc, text
from collections import defaultdict, Counter
from textblob import TextBlob
from tqdm import tqdm

from .database import (OfficeQuote, Character, DialogueLine,
                       setupDb, contextSession, create_db)

@click.command()
@click.argument('db_path', type=click.Path(readable=True))
def test(db_path):
    setupDb(db_path)
    print(analyzeCharacterDialogue("Michael"))


def analyzeCharacterDialogue(character_name):
    '''
    Do full dialogue analysis for a character
    '''
    lines = getLinesBySeasonByCharacter(character_name)
    analysis = analyzeLines(lines)
    analysis['episode_count'] = getEpisodeCount(character_name)
    return analysis


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


def getLinesBySeasonByCharacter(character_name):
    '''
    Get a list of (line, season) for each line spoken by a character.
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


def analyzeLines(lines_by_season):
    '''
    Analyze a list of lines on a per-season basis.

    returns: a dict of lists, the values of which are (per-season)
             line count, word count, sentence count, polarity, subjectivity
    '''
    textblobs = [TextBlob(' '.join(season_lines)) for season_lines in lines_by_season]
    word_counts, sentence_counts, polarity, subjectivity = zip(
        *[(len(tb.words), len(tb.sentences), tb.sentiment.polarity, tb.sentiment.subjectivity)
          for tb in tqdm(textblobs)])

    return {
        'lines': [len(season_lines) for season_lines in lines_by_season],
        'words': word_counts,
        'sentences': sentence_counts,
        'polarity': polarity,
        'subjectivity': subjectivity
    }



CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command('main_characters', context_settings=CONTEXT_SETTINGS)
@click.option('output_json', '-o',
              default="line_counts.json",
              type=click.Path(writable=True),
              help="Path to output json file.")
@click.option('--min_line_count', '-m', default=100, help="Filter characters with fewer lines.")
@click.argument('db_path', type=click.Path(readable=True))
def main_characters(db_path, output_json, min_line_count):
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
    for char in sum(characters, ())):
        print(char)

