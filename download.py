#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup, SoupStrainer, Doctype
import re

def getEpisodeQuotes(url):
    req = requests.get(url)
    req.raise_for_status()
    soup = BeautifulSoup(req.content, "lxml", parse_only=SoupStrainer("div", {"class": "quote"}))

    # remove font setting tags
    tags_to_remove = ("b", "i", "u")
    for tag in tags_to_remove:
        for match in soup.findAll(tag):
            match.unwrap()

    # remove all <br/> line break tags
    for linebreak in soup.findAll("br"):
        linebreak.extract()

    for quote in filter(lambda q: type(q) is not Doctype, soup):
        print(type(quote))
        break



root = "http://www.officequotes.net"
index = "{}/index.php".format(root)

req = requests.get(root)
req.raise_for_status()

eps_link_re = re.compile("no\d-\d+.php")
eps_links = filter(lambda link: hasattr(link, "href"), BeautifulSoup(req.content, "lxml", parse_only=SoupStrainer("a", href=eps_link_re)))

for link in eps_links:
    print(link["href"])
    getEpisodeQuotes("{}/{}".format(root, link["href"]))
    break


#naveps = soup.find_all("div", {"class": "navEp"})[0]
