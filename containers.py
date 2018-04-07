from collections.abc import Iterable
import attr

@attr.s
class Episode():
    number = attr.ib(validator=attr.validators.instance_of(int))
    season = attr.ib(validator=attr.validators.instance_of(int))
    scenes = attr.ib(validator=attr.validators.instance_of(Iterable), converter=list)

    def __str__(self):
        return "S{}E{}: {} scenes".format(self.season, self.number, len(self.scenes))

@attr.s
class Quote():
    speaker = attr.ib(validator=attr.validators.instance_of(str))
    line = attr.ib(validator=attr.validators.instance_of(str))

    def __str__(self):
        return "<Quote(speaker={}, line={})>".format(self.speaker, self.line)

@attr.s
class Scene():
    quotes = attr.ib(validator=attr.validators.instance_of(Iterable), converter=list)
    deleted = attr.ib(validator=attr.validators.instance_of(bool))

    def __str__(self):
        return "<Quote(speaker={}, line={})>".format(self.speaker, self.line)


