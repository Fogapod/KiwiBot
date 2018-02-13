class Logger:

    def __init__(self):
        self.VERBOSITY_SILENT = 0
        self.VERBOSITY_INFO   = 1
        self.VERBOSITY_DEBUG  = 2
        self.VERBOSITY_TRACE  = 3

        self.verbosity = self.VERBOSITY_INFO

    def info(self, text):
        if self.verbosity >= self.VERBOSITY_INFO:
            print(self._prepend(text, to_prepend='[INFO ]'))

    def debug(self, text):
        if self.verbosity >= self.VERBOSITY_DEBUG:
            print(self._prepend(text, to_prepend='[DEBUG]'))

    def trace(self, text):
        if self.verbosity >= self.VERBOSITY_TRACE:
            print(self._prepend(text, to_prepend='[TRACE]'))

    def _prepend(self, text, to_prepend='    '):
        return to_prepend + ('\n' + to_prepend).join(text.split('\n'))