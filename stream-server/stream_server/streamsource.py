import asyncio
import os
from typing import Generator, Union
from appdirs import AppDirs

DIRS = AppDirs("stream-server", "translation-pipeline")
STREAM_PATH = os.path.join(DIRS.user_state_dir, "stream.txt")


class StreamSource:
    def __init__(self, interval=2.0, path=STREAM_PATH, encoding="utf-8"):
        self.interval = interval
        self.path = STREAM_PATH
        self.seen = set()
        self.encoding = encoding

        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    @property
    async def text_events(self) -> Generator[Union[str, None], None, None]:
        while not os.path.exists(STREAM_PATH):
            await asyncio.sleep(self.interval)
            yield None

        while True:
            try:
                for event in self.events_raw:
                    yield event
                # TODO: would be nice to subscribe to file change
                # events here instead of polling
                await asyncio.sleep(self.interval)
                yield None
            except IOError:
                if not os.path.exists(STREAM_PATH):
                    return
                raise

    @property
    def events_raw(self) -> Generator[str, None, None]:
        if not os.path.exists(self.path):
            return

        with open(self.path, "rt", encoding=self.encoding) as f:
            for line in f:
                (ident, content) = line.split(":", 1)
                if ident in self.seen:
                    continue
                self.seen.add(ident)
                yield content
