from session_interface import SessionInterface
from tables import Character, DialogueLine, OfficeQuote


class DbInterface():
    def __init__(self, db_file="db.sqlite"):
        self.session_interface = SessionInterface(db_file)


    def addEpisode(self, episode):
        """
        Convert each quote in an episode into the database schema class
            and write them to the database.
        """
        for quote in episode.quotes:
            db_quote = OfficeQuote(
                season=episode.season,
                episode=episode.number,
                deleted=scene.deleted)
            db_quote.speaker = self.getOrCreate(Character, name=quote.speaker)
            db_quote.line = DialogueLine(content=quote.line)

            self.session_interface.add(quote)

    def getCharacterById(self, char_id):
        with self.session_interface.session_scope() as session:
            session.query(Character).filter(Character.id==char_id)

    def getCharacterByName(self, char_name):
        with self.session_interface.session_scope() as session:
            session.query(Character).filter(Character.name==char_name)

