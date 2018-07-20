import re

req_headers = {"User-Agent":
    ("Mozilla/5.0 (X11; CrOS x86_64 10032.86.0) "
     "AppleWebKit/537.36 (KHTML, like Gecko) "
     "Chrome/63.0.3239.140 Safari/537.36")
}

index_url = "http://www.officequotes.net/index.php"

eps_href_re = re.compile("no(\d)-(\d+).php")

