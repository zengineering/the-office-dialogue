import requests
from bs4 import BeautifulSoup

root = "http://www.officequotes.net/index.php"

req = requests.get(root)
r.raise_for_status()

soup = BeautifulSoup(r.content, "lxml")

naveps = soup.find_all("div", {"class": "navEp"})[0]
