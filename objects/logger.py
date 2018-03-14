import time

from sys import stdout
from os.path import exists


class Logger:

    _logger = None

    def __init__(self, filename=None):
        Logger._logger = self

        self.VERBOSITY_SILENT = 0
        self.VERBOSITY_INFO   = 1
        self.VERBOSITY_DEBUG  = 2
        self.VERBOSITY_TRACE  = 3

        self.verbosity = self.VERBOSITY_INFO

        self._files = [stdout, ]

        if filename is not None:
            self._files.append(open(filename, 'a'))

    def add_file(self, filename):
        if filename is None:
            return

        self._files.append(open(filename, 'a'))

    def info(self, *args):
        if self.verbosity >= self.VERBOSITY_INFO:
            text = ' '.join(args)
            to_prepend = time.strftime('[%H:%M:%S]', time.localtime()) + '[INFO ]'
            self._log(self._prepend(text, to_prepend=to_prepend))

    def debug(self, *args):
        if self.verbosity >= self.VERBOSITY_DEBUG:
            text = ' '.join(args)
            to_prepend = time.strftime('[%H:%M:%S]', time.localtime()) + '[DEBUG]'
            self._log(self._prepend(text, to_prepend=to_prepend))

    def trace(self, *args):
        if self.verbosity >= self.VERBOSITY_TRACE:
            text = ' '.join(args)
            to_prepend = time.strftime('[%H:%M:%S]', time.localtime()) + '[TRACE]'
            self._log(self._prepend(text, to_prepend=to_prepend))
     
    def _log(self, text):
        for f in self._files:
            print(text, file=f)
            f.flush()

    @staticmethod
    def get_logger():
        return Logger._logger
        
    def _prepend(self, text, to_prepend='    '):
        return to_prepend + ('\n' + to_prepend).join(text.split('\n'))