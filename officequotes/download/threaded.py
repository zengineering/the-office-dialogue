from threading import Thread, Event, current_thread
from sys import stderr
from urllib.parse import urljoin
from sqlalchemy.sql import select
from sqlalchemy import func

from officequotes.database import (
    addQuote, contextSession, DialogueLine, Character, OfficeQuote, engineConnection)
from .fetch import episodeFactory

class StoppingThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()


def fetchAndParse(url_q, episode_q, failed_q, eps_href_re, index_url):
    '''
    Pop a url from the url queue
    Download and parse the episode page at that url
    Push the parsed result into the episode queue
    If parsing or downloading fails, put it in the failed queue
    '''
    while not url_q.empty():
        eps_url = url_q.get()
        episode = episodeFactory(urljoin(index_url, eps_url), eps_href_re)
        episode_q.put(episode)
        if episode is None:
            failed_q.put(eps_url)

    while not failed_q.empty():
        episode_q.put(episodeFactory(urljoin(index_url, eps_url), eps_href_re))



def writeToDatabase(queue):
    '''
    Store all quotes for an episode using a single database commit
    '''
    with contextSession() as session:
        last_line_id = session.query(func.max(DialogueLine.id)).one_or_none()
        if last_line_id is None:
            last_line_id = 1

    while not current_thread().stopped:
        if not queue.empty():
            episode = queue.get_nowait()
            if episode:
                writeEpisodeToDb(episode, last_line_id)


def writeEpisodeToDb(episode, last_line_id):
    '''
    Write all quotes in an episode to the database
    '''
    conn = engineConnection()
    # write dialogue lines first
    conn.execute(
        DialogueLine.__table__.insert(),
        [{"id": i+last_line_id, "content": quote.line} for i, quote in episode.quotes]
    )

    speaker_ids = []
    for quote in episode.quotes:
        speaker_id = conn.execute(
            select([Character.__table__.id]).where(Character.__table__.name == quote.speaker))
        if speaker_id is not None:
            speaker_ids.append(speaker_id)
        else:
            speaker_ids.append(
                conn.execute(Character.__table__.insert().values(name=quote.speaker)).lastrowid)

    conn.execute(
        OfficeQuote.__table__.insert(),
        [{'season': episode.season,
          'episode': episode.number,
          'deleted': quote.deleted,
          'speaker_id': speaker_ids[i],
          'line_id': i+last_line_id
         } for i, quote in enumerate(episode.quotes)]
    )


def progress(url_q, episode_q):
    '''
    Show the progress of episode downloads
    '''
    total_episodes = url_q.qsize()
    while not url_q.empty():
        print("Downloading {:>4}/{:>4}".format(total_episodes - url_q.qsize(), total_episodes),
              end="\r")
    print()

    while not episode_q.empty():
        print("Storing {:>4}/{:>4}".format(total_episodes - episode_q.qsize(), total_episodes),
              end="\r", file=stderr)
    print()
