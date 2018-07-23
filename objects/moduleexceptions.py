class CommandCancelled(Exception):
	pass

class ModuleCallError(Exception):
    pass


class GuildOnly(ModuleCallError):
    pass


class NSFWPermissionDenied(ModuleCallError):
    pass


class NotEnoughArgs(ModuleCallError):
    pass


class TooManyArgs(ModuleCallError):
    pass


class MissingPermissions(ModuleCallError):
    def __init__(self, *missing):
        self.missing = missing