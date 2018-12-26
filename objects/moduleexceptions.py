class ModuleCallError(Exception):
    pass


class GuildOnly(ModuleCallError):
    pass


class NSFWPermissionDenied(ModuleCallError):
    pass


class ArgParseError(ModuleCallError):
    pass


class ArgCheckError(ArgParseError):
    pass


class NotEnoughArgs(ModuleCallError):
    pass


class TooManyArgs(ModuleCallError):
    pass


class MissingPermissions(ModuleCallError):
    def __init__(self, *missing):
        self.missing = missing


class Ratelimited(ModuleCallError):
    def __init__(self, ttl):
        self.time_left = ttl
