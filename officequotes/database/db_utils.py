from .session_interface import contextSession, db_add, db_getOrCreate
from .tables import Character, DialogueLine, OfficeQuote


def addQuote(season, episode, deleted, speaker, line):
    quote = OfficeQuote(
        season=season,
        episode=episode,
        deleted=deleted
    )
    quote.speaker = db_getOrCreate(Character, name=speaker)
    quote.line = DialogueLine(content=line)
    db_add(quote)


def getCharacter(**kwargs):
    if not kwargs:
        return None
    else:
        with contextSession() as session:
            q = session.query(Character).filter_by(**kwargs).all()
            session.expunge_all()
        return q

