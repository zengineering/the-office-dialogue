from .session_interface import contextSession, db_add, db_getOrCreate
from .tables import Character, DialogueLine, OfficeQuote


def addEpisode(episode):
    """
    Convert each quote in an episode into the database schema class
        and write them to the database.
    """
    for quote in episode.quotes:
        db_quote = OfficeQuote(
            season=episode.season,
            episode=episode.number,
            deleted=quote.deleted)
        db_quote.speaker = db_getOrCreate(Character, name=quote.speaker)
        db_quote.line = DialogueLine(content=quote.line)

        db_add(quote)


def getCharacter(**kwargs):
    if not kwargs:
        return None
    else:
        with contextSession() as session:
            q = session.query(Character).filter_by(**kwargs).all()
            session.expunge_all()
        return q


def getCharacterByName(char_name):
    with contextSession() as session:
        q = session.query(Character).filter(Character.name==char_name).all()
    return q

    #def getCharacterByAttr(attr_name):
    #    try:
    #        attr = getattr(Chracter, attr_name)
    #        with contextSession() as session:
    #            session.query(Character).filter(Character.name==char_name)
    #    except AttributeError:
    #        return None
