import json
import time
from threading import Thread

from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer


SLEEP_HEADER = 'X-Sleep-For'

DEFAULT_TEST_PORT = 13807
DEFAULT_TEST_HOST = 'localhost'
DEFAULT_TEST_IP = '127.0.0.1'
DEFAULT_TEST_URL = 'http://{}:{}'.format(DEFAULT_TEST_HOST, DEFAULT_TEST_PORT)


def _read_request_body(rfile):
    request_body = b''
    while True:
        body_bytes = rfile.read(100)
        if body_bytes:
            request_body += body_bytes
        else:
            break
    return request_body


def _maybe_sleep(headers):
    sleep_time = headers.get(SLEEP_HEADER)
    if sleep_time is not None:
        time.sleep(int(sleep_time))


def handle(self):
    """Generic handler for all HTTP methods of the testing HTTP server. Echos
    back all received headers with an 'X-' prefix and adds the length of the
    body received.
    """
    _maybe_sleep(self.headers)

    self.send_response(code=self.headers.get('X-Expected-Code', 200))

    for header, value in self.headers.items():
        self.send_header('X-{}'.format(header), value)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()

    self.wfile.write(
        json.dumps({
            'body_length': len(_read_request_body(self.rfile)),
            'method': self.command,
        }).encode('utf-8')
    )


class HandlerMeta(type):

    METHODS = ('DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT')

    def __init__(cls, name, bases, attrs):
        for method in cls.METHODS:
            setattr(cls, 'do_{}'.format(method), handle)
        return super(HandlerMeta, cls).__init__(name, bases, attrs)


class Handler(BaseHTTPRequestHandler, metaclass=HandlerMeta):

    def log_message(self, format, *args):
        # Turns off normal logging
        pass


def run_server(host=DEFAULT_TEST_HOST, port=DEFAULT_TEST_PORT):
    httpd = HTTPServer((host, port), Handler)
    httpd.serve_forever()


def run_server_in_thread():
    thread = Thread(target=run_server, daemon=True)
    thread.start()


if __name__ == '__main__':
    run_server()
