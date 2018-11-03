class EmptyImage(Exception):
    def __str__(self):
        return 'Can\'t handle image without url or bytes'


class Image:
    __slots__ = ('_ctx', 'type', 'extension', 'url', 'bytes', 'error', )

    def __init__(self, ctx, type=None, extension=None, url=None, bytes=None, error=None):
        self._ctx = ctx

        self.type = type
        self.extension = extension
        self.url = url
        self.bytes = bytes
        self.error = error

    async def ensure(self, raise_on_error=False, timeout=10):
        """Ensures image bytes are downloaded"""

        if self.bytes or self.error:
            return self

        if not self.url:
            raise EmptyImage

        try:
            async with self._ctx.bot.sess.get(
                    self.url, timeout=timeout, raise_for_status=True,
                    proxy=self._ctx.bot.get_proxy()) as r:

                self.bytes = await r.read()
        except Exception as e:
            if raise_on_error:
                raise
            else:
                self.error = f'Error downloading image: {e}'

        return self

