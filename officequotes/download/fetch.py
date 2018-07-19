import requests
import re
from sys import stderr
from .parse import parseEpisode
from .dataclasses import Episode

req_headers = {"User-Agent":
    ("Mozilla/5.0 (X11; CrOS x86_64 10032.86.0) "
     "AppleWebKit/537.36 (KHTML, like Gecko) "
     "Chrome/63.0.3239.140 Safari/537.36")
}

def fetchContent(url):
    '''
    Request a url and return the contents.
    '''
    req = requests.get(url, headers=req_headers)
    req.raise_for_status()
    return req.text


def episodeFactory(eps_url, eps_url_pattern):
    '''
    Fetch the content from an episode page and convert it to an Episode instance.
    '''
    eps = None
    try:
        season, episode = map(int, re.search(eps_url_pattern, eps_url).groups())
        content = fetchContent(eps_url)
        if content:
            quotes = parseEpisode(content)
            eps = Episode(episode, season, quotes)
    except requests.RequestException as e:
        print("Request for {} failed:\n\t{}".format(eps_url, e), file=stderr)

    finally:
        return eps

