from objects.modulebase import ModuleBase
from objects.permissions import PermissionEmbedLinks

from discord import Colour, File, Embed

from PIL import Image, ImageColor

from io import BytesIO


class Module(ModuleBase):

    usage_doc = '{prefix}{aliases} <colour>'
    short_doc = 'Display information about given colour'

    name = 'colourinfo'
    aliases = (name, 'colorinfo')
    category = 'Utils'
    bot_perms = (PermissionEmbedLinks(), )
    min_args = 1

    async def on_call(self, msg, args, **flags):
        try:
            rgb = ImageColor.getrgb(args[1:])
            colour = Colour.from_rgb(*rgb)
        except ValueError as e:
            return '{warning} Not a colour'

        bytes_img = BytesIO()
        img = Image.new('RGB', (100, 100), rgb)
        img.save(bytes_img, format='JPEG')
        bytes_img.seek(0)
        file = File(bytes_img, filename='img.jpg')

        e = Embed(colour=colour, title=str(colour))
        e.add_field(name='Decimal value', value=colour.value)
        e.set_image(url='attachment://img.jpg')

        await self.send(msg, embed=e, file=file)