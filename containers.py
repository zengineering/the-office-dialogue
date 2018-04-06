from collections import namedtuple

Episode = namedtuple("Episode", ['number', 'season', 'scenes'])
Scene = namedtuple("Scene", ['quotes', 'deleted'])
Quote = namedtuple("Quote", ['speaker', 'line'])

