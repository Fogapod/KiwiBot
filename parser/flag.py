import inspect

from parser import Argument
from parser.converters import String, Bool

from objects.moduleexceptions import ArgParseError, ArgCheckError


class Flag(Argument):

    def __init__(self, name, alias, descr='', hint=None, converter=String(), checks=(), hidden=False):
        self.name = name
        self.alias = alias
        self.description = descr

        if isinstance(converter, type):
            self.converter = converter()
        else:
            self.converter = converter

        if hint is None and not isinstance(self.converter, Bool):
            self.hint = self.converter.pretty_name.lower()
        else:
            self.hint = hint

        self.checks = checks
        self.hidden = hidden

    def doc_line(self):
        base = f'  [--{self.name}|-{self.alias}]'
        if self.hint is not None:
            base += f' <{self.hint}>: '
        else:
            base += ': '

        return base + self.description

    def __str__(self):
        return repr(self)
