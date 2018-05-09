## Tools to scrape http://officequotes.net/ and download all dialogue.

### Usage
```bash
    $ ./run.sh
```

*run.sh* will:
- Download http://officequotes.net/index.php
- Scrape the index page for links to each episode page
- Download each episode page
- Extract the dialogue into lightweight objects
- Write all dialogue objects to a SQLite database: *the-office-quotes.sqlite*


### Structure

#### *download.py*
The "main" module. Top-level command/control, thread management, and (eventually) commandline arguments.

#### *parse.py*
BeautifulSoup-based functions for parsing webpage content into lighweight objects.

#### *containers.py*
attr-based convenience classes for organizing dialogue between download and storage.

#### *database.py*
SQLAlchemy-based classes for SQLite/ORM interaction.
