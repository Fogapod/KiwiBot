from asyncio import TimeoutError

STATIC_FORMATS = ('png', 'jpg', 'jpeg', 'webp')
DEFAULT_STATIC_FORMAT = 'png'

MAX_CONTENT_LENGTH = 7000000

class EmptyImage(Exception):
    def __str__(self):
        return 'Can\'t handle image without url or bytes'


class Image:
    __slots__ = ('_ctx', 'type', 'extension', 'url', 'bytes', 'error', '_use_proxy')

    def __init__(self, ctx, type=None, extension=None, url=None, bytes=None, error=None, use_proxy=True):
        self._ctx = ctx

        self.type = type
        self.extension = extension
        self.url = url if url is None else str(url)
        self.bytes = bytes
        self.error = error

        self._use_proxy = use_proxy

    def __str__(self):
        return self.url or ''

    def __repr__(self):
        return f"<Image type='{self.type}' extension='{self.extension}' url='{self.url}' error='{self.error}'>"

    async def ensure(self, raise_on_error=False, timeout=5):
        """Ensures image bytes are downloaded"""

        if self.bytes or self.error:
            return self

        if not self.url:
            raise EmptyImage

        try:
            proxy = self._ctx.bot.get_proxy() if self._use_proxy else None

            async with self._ctx.session.get(
                    self.url, timeout=timeout, raise_for_status=True,
                    proxy=proxy) as r:

                if (r.content_length or 0) > MAX_CONTENT_LENGTH:
                    self.error = f'Content is too big'
                    return self

                extension = r.content_type.rpartition('/')[-1]
                if extension == 'gif':
                    if self.type == 'url/static':
                        self.error = 'Found gif, gif images are not allowed'
                        return self
                elif extension not in STATIC_FORMATS:
                    self.error = f'Unknown file extension: **{r.content_type}**, expected one of **{", ".join(STATIC_FORMATS)}**'
                    return self

                self.bytes = await r.read()
        except (Exception, TimeoutError) as e:
            if raise_on_error:
                raise
            else:
                self.error = 'Download error: '
                if isinstance(e, TimeoutError):
                    self.error += f'Timeout: **{timeout}s**'
                else:
                    self.error += str(e)

        return self
