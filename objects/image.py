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

    async def ensure(self, raise_on_error=False, timeout=10):
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

                self.bytes = await r.read()
        except Exception as e:
            if raise_on_error:
                raise
            else:
                self.error = f'Error downloading image: {e}'

        return self
