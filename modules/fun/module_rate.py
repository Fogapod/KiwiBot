from objects.modulebase import ModuleBase

from utils.funcs import find_user

from hashlib import sha256


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subject>'
    short_doc = 'Perform a comprehensive research and rate given subject.'

    name = 'rate'
    aliases = (name, )
    required_args = 1

    async def on_call(self, msg, args, **flags):
        subject = args[1:]
        user = await find_user(subject, msg, self.bot)

        if user is not None:
            target = str(user.id)
        else:
            target = subject

        return 'I rate **{0}** {1}/10'.format(user.display_name if user else subject, sum(int(ord(c)) for c in sha256(target.upper().encode()).hexdigest()) % 11)