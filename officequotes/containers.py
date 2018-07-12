from collections.abc import Iterable
import attr

@attr.s(frozen=True)
class Episode():
    number = attr.ib(validator=attr.validators.instance_of(int))
    season = attr.ib(validator=attr.validators.instance_of(int))
    scenes = attr.ib(validator=attr.validators.instance_of(Iterable),
                     converter=lambda itr: list(filter(lambda i: len(i.quotes) > 0, itr)))

    def __str__(self):
        return "<Episode(S{}E{}: {} scenes)>".format(self.season, self.number, len(self.scenes))

@attr.s(frozen=True)
class Quote():
    speaker = attr.ib(validator=attr.validators.instance_of(str))
    line = attr.ib(validator=attr.validators.instance_of(str))
    deleted = attr.ib(validator=attr.validators.instance_of(bool))

    def __str__(self):
        return "<Quote(speaker={}, line={}, deleted={})>".format(self.speaker, self.line, self.deleted)


