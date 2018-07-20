from threading import Thread, Event, current_thread
from sys import stderr
from urllib.parse import urljoin

from officequotes.database import addQuote, makeQuote, contextSession
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


def writeToDatabase(queue, commit_each=True):
    '''
    Write episodes in the queue to a database until the current thread is stopped
    '''
    return writeToDatabaseMultiCommit(queue) if commit_each else writeToDatabaseSingleCommit(queue)


def writeToDatabaseSingleCommit(queue):
    '''
    Store all quotes for an episode using a single database commit
    '''
    successful = 0
    with contextSession() as session:
        while not current_thread().stopped:
            if not queue.empty():
                episode = queue.get_nowait()
                if episode:
                    for quote in episodeQuotes(episode):
                        session.add(quote)
                        successful += 1
    return successful


def episodeQuotes(episode):
    '''
    Make a generator of database-model Quote's for an episode
    '''
    return (makeQuote(episode.season, episode.number, *quote.to_tuple())
            for quote in episode.quotes)


def writeToDatabaseMultiCommit(queue):
    '''
    Store all quotes for an episode using individual database commits
    '''
    successful = 0
    while not current_thread().stopped:
        if not queue.empty():
            episode = queue.get_nowait()
            if episode:
                writeEpisodeToDb(episode)
                successful += 1
    return successful


def writeEpisodeToDb(episode):
    for quote in episode.quotes:
        addQuote(episode.season, episode.number, *quote.to_tuple())


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
