# The Office Dialogue

![the_office](https://i.ytimg.com/vi/8GxqvnQyaxs/maxresdefault.jpg)

[The Office](https://www.imdb.com/title/tt0386676/) is a fantastic show; 
this project does some basic analysis of the dialogue from the show.
The data is sourced from [here](http://officequotes.net/).


### Structure

- **officequotes/** is a Python package containing all of the tools.
- **tests/**, as one might expect, contains tests for the *officequotes* package.
- **data/** holds the results of running the tools. More on this later.
- **officequotes.sh** is a convenience script for running the *officequotes* tools.


### TLDR:
Look at **/data/analysis.json**. 

Slightly longer:

```console
dwight@dm1:-$ make install && make all
```

...then look at the results in **/data/analysis.json**.


### Workflow
A makefile is provided for convenience. Dive into it to see the package-level commands it runs.


#### Setup
To get started, create a Python environment via virtualenv/pipenv/conda/etc, then run:

```console
dwight@dm1:-$ make install
```

This will install all of the required packages via pip, along with the required corpora for text analysis.


#### Testing
Next, to make sure things are OK and get some nice green text:

```console
dwight@dm1:-$ make test
```

This runs the tests in **tests/** via [pytest](https://docs.pytest.org/en/latest/).


#### Download
For this repo, **/data/json** is actual a [submodule](https://github.com/zengineering/the-office), so there isn't *really* a need to run this step.
If you like your data fresh though, make sure you've got an internet connection and run

```console
dwight@dm1:-$ make download
```

...to download every episode page, parse it, and store the results in **/data/json**.
It will also process the downloaded files, applying corrections to name misspellings and inconsistencies (e.g. Michel -> Michael).


#### Database

A directory of directories full of JSON is nice for git storage and for browsing, but for the analysis work we'll want a database.

```console
dwight@dm1:-$ make database
```

At the end you'll have **/data/officequotes.sqlite**, a SQLite database with three tables storing all of the dialogue from **/data/json**.


#### Analysis

Now for the exciting part!

```console
dwight@dm1:-$ make analysis
```

This runs two tools.
The first produces a list of "main characters", i.e. characters that have more than 100 lines of dialogue througout the series.
The second analyzes all of the dialogue for each of the main characters, producing (for each season): 
- Number of lines spoken.
- Number of sentences spoken.
- Number of words spoken.
- The polarity of the character's dialogue (negative or positive speech, on a [-1.0, 1.0] scale).
- The subjectivity of the character's dialgoue on a scale from 0.0 (completely objective) up to 1.0 (completely subjective).


#### Results 

At this point you've run all the tools, and the results are in **/data/analysis.json**.
That file already exists in the repo (and shouldn't change after running the tools), but if you skipped the [TLDR](https://github.com/zengineering/the-office-dialogue/blob/master/README.md#tldr) you've got your own fresh copy now.

Some of the results are visualized [here](https://zengineering.github.io/2018/06/04/the-office-dialogue.html).
Soon I'll have a more exciting website for visualizing all of the data.


### Details

If you want more information than what/where the data is and what ```make``` commands to run, you're in the right place.

There are five tools in the *officequotes* package. 

If you run them directly via Python make sure one of the following is true: 
1. You're in the repo's root directory
2. The *officequotes* package is installed via pip
3. PYTHONPATH is set to the root of the repo

Alternatively, **officequotes.sh** should take care of that for you.
It finds the directory it's located in, sets ```PYTHONPATH``` and calls ```python -m officequotes```, forwarding all arguments.


```console
dwight@dm1:-$ python -m officequotes
Usage: officequotes [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  analyze_character  Analyze all dialogue for a character.
  corrections        Make name corrections in JSON.
  create_db          Create database from JSON files.
  download           Download all dialogue from The Office.
  main_characters    Return a list of main characters.
```

To get help and a more detailed description of each tool, run:
```console
dwight@dm1:-$ python -m officequotes <command> --help
```

#### Notables
- If you have a beloved minor character (e.g. Bob Vance) and want their stats, just run ```./officequotes.sh analyze_character <name>```
- *corrections* is based on **/officequotes/resources/name_corrections.json**, so if you've got more corrections put them in that file.
- *corrections* and *create_db* take a directory as an argument, and expect the same structure/format as the directory produced by *download*
- *main_characters*'s ```-m``` option specified the minimum line count that dictates who is a "main character"
- *analyze_character* takes a variable number of character names, and outputs JSON analysis for each of them. If none are specified, it reads the character names from stdin, so you can pipe the output of *main_characters* into it.
