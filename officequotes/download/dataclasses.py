import attr

@attr.s(frozen=True)
class Episode():
    number = attr.ib(validator=attr.validators.instance_of(int))
    season = attr.ib(validator=attr.validators.instance_of(int))
    quotes = attr.ib(validator=attr.validators.instance_of(list))

    def __str__(self):
        return "<Episode(S{}E{}: {} quotes)>".format(self.season, self.number, len(self.quotes))

@attr.s(frozen=True)
class Quote():
    speaker = attr.ib(validator=attr.validators.instance_of(str))
    line = attr.ib(validator=attr.validators.instance_of(str))
    deleted = attr.ib(validator=attr.validators.instance_of(bool))

    def __str__(self):
        return "<Quote(speaker={}, line={}, deleted={})>".format(self.speaker, self.line, self.deleted)

    def to_tuple(self):
        attr.astuple(self)
