from .session_interface import sessionScope, db_add, db_getOrCreate
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


def getCharacterById(char_id):
    with sessionScope() as session:
        q = session.query(Character).filter(Character.id==char_id).first()
    return q


def getCharacterByName(char_name):
    with sessionScope() as session:
        q = session.query(Character).filter(Character.name==char_name).all()
    return q

    #def getCharacterByAttr(attr_name):
    #    try:
    #        attr = getattr(Chracter, attr_name)
    #        with sessionScope() as session:
    #            session.query(Character).filter(Character.name==char_name)
    #    except AttributeError:
    #        return None
