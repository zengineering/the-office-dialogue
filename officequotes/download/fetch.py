import requests
from urllib.parse import urljoin
from sys import stderr


def fetchContent(url):
    '''
    Request a url and return the contents.
    '''
    req = requests.get(url, headers=req_headers)
    req.raise_for_status()
    return req.text


def episodeFactory(eps_url, eps_url_pattern, index_url):
    '''
    Fetch the content from an episode page and convert it to an Episode instance.
    '''
    try:
        season, episode = map(int, re.fullmatch(eps_url_pattern, eps_url).groups())
        url = urljoin(index_url, eps_url)
        content = fetchContent(url)
        if content:
            quotes = parseEpisode(content)
            return Episode(episode, season, quotes)
        else:
            return None
    except requests.RequestException as e:
        print("Request for {} failed:\n\t{}".format(eps_url, e), file=stderr)
    except Exception as e:
        print("Episode from url {} failed:\n\t{}".format(eps_url, e), file=stderr)


def fetchAndParse(url_q, episode_q, failed_q, eps_href_re, index_url):
    '''
    Pop a url from the url queue
    Download and parse the episode page at that url
    Push the parsed result into the episode queue
    If parsing or downloading fails, put it in the failed queue
    '''
    while not url_q.empty():
        eps_url = url_q.get()
        episode = episodeFactory(eps_url, eps_href_re, index_url)
        episode_q.put(episode)
        if episode is None:
            failed_q.put(eps_url)

