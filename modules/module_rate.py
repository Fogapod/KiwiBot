from modules.modulebase import ModuleBase

from utils.helpers import find_user

from hashlib import sha256


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <subject>'
    short_doc = 'Perform a comprehensive research and rate given subject.'

    name = 'rate'
    aliases = (name, )
    required_args = 1

    async def on_call(self, msg, *args, **flags):
        subject = msg.content.partition(args[0])[2].lstrip()
        user = await find_user(subject, msg, self.bot)

        if user is not None:
            target = str(user.id)
        else:
            target = subject

        return 'I rate **{0}** {1}/10'.format(user.display_name if user else subject, sum(int(ord(c)) for c in sha256(target.upper().encode()).hexdigest()) % 11)