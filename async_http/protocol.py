import asyncio
import time
from concurrent.futures import TimeoutError as _BuiltInTimeoutError

from async_http.errors import TimeoutError
from async_http.http_utils import parse_http_response


class Future:

    def __init__(self, coro_future):
        self.coro_future = coro_future

    def result(self, timeout=None):
        try:
            response = self.coro_future.result(timeout=timeout)
            return parse_http_response(response)
        except _BuiltInTimeoutError:
            raise TimeoutError()


class Protocol(asyncio.Protocol):
    """TCP protocol instance that immediately writes content to the socket."""

    def __init__(self, content):
        self._content = content
        self.finished = False
        # TODO should be BytesIO?
        self.response = b''
        self._transport = None
        self._start_time = time.time()
        self._end_time = None

    def connection_made(self, transport):
        transport.write(self._content.encode())
        # Writing EOF appears to force external servers (e.g. google) to close
        # the connection on their side.
        transport.write_eof()
        self._transport = transport

    def data_received(self, data):
        # Since this is a streaming socket, this can be called multiple times
        # before the server sends EOF.
        self.response += data

    def eof_received(self):
        self._transport.close()
        self.finished = True

    def connection_lost(self, exc):
        self.finished = True
        self._end_time = time.time()
