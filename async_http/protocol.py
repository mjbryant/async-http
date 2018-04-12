import asyncio
import time


class Future:

    def __init__(self, coro_future):
        self.coro_future = coro_future

    def result(self, timeout=None):
        response = self.coro_future.result(timeout=timeout)
        return response


class Protocol(asyncio.Protocol):
    """TCP protocol instance that immediately writes content to the socket."""

    UNSET = -1

    def __init__(self, content):
        self._content = content
        self.finished = False
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
