#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup, SoupStrainer
import re

root = "http://www.officequotes.net/index.php"

req = requests.get(root)
req.raise_for_status()

eps_link_re = re.compile("no\d-\d+.php")
eps_links = filter(lambda link: hasattr(link, 'href'), BeautifulSoup(req.content, "lxml", parse_only=SoupStrainer('a', href=eps_link_re)))

for link in eps_links:
    print(link['href'])

#naveps = soup.find_all("div", {"class": "navEp"})[0]
