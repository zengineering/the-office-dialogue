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
        lines = (session.query(Character.name, OfficeQuote.season, DialogueLine.line)
                        .filter(Character.name == character_name)
                        .join(OfficeQuote)
                        .join(DialogueLine)
                        .all())

    lines_by_season = [[] for _ in range(9)]
    for _, season, line in lines:
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
@click.command('analyze', context_settings=CONTEXT_SETTINGS)
@click.option('output_json', '-o',
              default="line_counts.json",
              type=click.Path(writable=True),
              help="Path to output json file.")
@click.option('--min_line_count', '-m', default=100, help="Filter characters with fewer lines.")
@click.argument('db_path', type=click.Path(readable=True))
def analyze(db_path, output_json, min_line_count):
    '''
    Count the total number of lines by each character.

    Using the datbase created by officequotes.create_db,
    produce a JSON file with each character's name,
    database id, and total number of lines spoken.
    '''
    setupDb(db_path)
    with contextSession() as session:
        freq = func.count(OfficeQuote.speaker_id).label('freq')
        line_counts = (
            session.query(OfficeQuote.season, Character.name, freq)
            .join(Character)
            .group_by(OfficeQuote.speaker_id, OfficeQuote.season)
            .all()
        )

    # parse query result into {character: {season: line count}}
    char_line_counts = defaultdict(dict)
    for season, name, line_count in line_counts:
        char_line_counts[name][season] = line_count

    # filter to characters with a significant total number of lines
    char_line_counts = {name: seasons for name, seasons in char_line_counts.items()
                             if sum(seasons.values()) > min_line_count}

    # write to json
    with open(output_json, 'w') as f:
        json.dump(char_line_counts, f, indent=4)

