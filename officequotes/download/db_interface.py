from database import addQuote


def writeEpisodeToDb(episode):
    for quote in episode.quotes:
        addQuote(episode.season, episode.number, *quote.to_tuple())


