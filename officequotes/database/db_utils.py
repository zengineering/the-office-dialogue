from .session_interface import contextSession, db_add, db_getOrCreate
from .tables import Character, DialogueLine, OfficeQuote


def addQuote(season, episode, speaker, line, deleted):
    '''
    Add a quote to the database (with a new character if necessary).
    '''
    quote = OfficeQuote(
        season=season,
        episode=episode,
        deleted=deleted
    )
    quote.speaker = db_getOrCreate(Character, name=speaker)
    quote.line = DialogueLine(content=line)
    db_add(quote)


def makeQuote(season, episode, speaker, line, deleted):
    '''
    Make a Quote
    '''
    quote = OfficeQuote(
        season=season,
        episode=episode,
        deleted=deleted
    )
    quote.speaker = db_getOrCreate(Character, name=speaker)
    quote.line = DialogueLine(content=line)
    return quote


def getCharacter(**kwargs):
    '''
    Retrieve a Character from the database
    '''
    if not kwargs:
        return None
    else:
        with contextSession() as session:
            q = session.query(Character).filter_by(**kwargs).one()
            session.expunge_all()
        return q

