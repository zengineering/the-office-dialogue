from collections.abc import Iterable
class Episode():
    def __init__(self, number, season, scenes):
        if not isinstance(number, int):
            raise ValueError("Episode arg1 expects an int; got a {}".format(type(number)))
        if not isinstance(season, int):
            raise ValueError("Episode arg2 expects an int; got a {}".format(type(season)))
        if not isinstance(scenes, Iterable):
            raise ValueError("Episode arg3 expects an Iterable; got a {}".format(type(scenes)))

        self.number = number
        self.season = season
        self.scenes = list(scenes)

    def __repr__(self):
        return "<Episode(number={}, season={}, scenes={})>".format(self.number, self.seasons, self.scenes)

    def __str__(self):
        return "S{}E{}: {} scenes".format(self.season, self.number, len(self.scenes))


class Scene():
    def __init__(self, quotes, deleted):
        if not isinstance(quotes, Iterable):
            raise ValueError("Episode arg1 expects an Iterable; got a {}".format(type(quotes)))
        if not isinstance(deleted, bool):
            raise ValueError("Episode arg2 expects a bool; got a {}".format(type(deleted)))

        self.quotes = list(quotes)
        self.deleted = deleted

    def __repr__(self):
        return "<Scene(quotes={}, deleted={})>".format(self.quotes, self.deleted)


class Quote():
    def __init__(self, speaker, line):
        if not isinstance(speaker, str):
            raise ValueError("Episode arg1 expects a str; got a {}".format(type(speaker)))
        if not isinstance(line, str):
            raise ValueError("Episode arg2 expects a str; got a {}".format(type(line)))

        self.speaker = speaker
        self.line = line

    def __repr__(self):
        return "<Quote(speaker={}, line={})>".format(self.speaker, self.line)

