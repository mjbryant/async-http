import json
from http.client import HTTPResponse
from io import BytesIO

from async_http import __version__
from async_http.errors import RequestBodyNotBytes


DEFAULT_USER_AGENT = 'async-http/{}'.format(__version__)


class _FakeSocket:
    def __init__(self, response_bytes):
        self._file = BytesIO(response_bytes)

    def makefile(self, *args, **kwargs):
        return self._file


class Response:
    """Lightweight HTTP response object"""
    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self._parsed_json = None

    def json(self):
        if self._parsed_json is not None:
            return self._parsed_json
        # TODO should probably look for a content-encoding header
        self._parsed_json = json.loads(self.body.decode())
        return self._parsed_json


def parse_http_response(raw_bytes):
    """Pretty hacky way to parse an HTTP response using the python standard
    library http utilities. Probably should be replaced at some point.
    """
    f = _FakeSocket(raw_bytes)
    response = HTTPResponse(f)
    response.begin()
    return Response(
        status_code=response.status,
        headers=dict(response.getheaders()),
        body=response.read(len(raw_bytes)),  # Reads slightly too many bytes
    )


def _add_host(http_message, headers, host):
    if not (
        'host' in headers or
        'Host' in headers or
        b'host' in headers or
        b'Host' in headers
    ):
        _write_header(http_message, b'Host', host)


def _add_user_agent(http_message, headers):
    if not (
        'user-agent' in headers or
        'User-Agent' in headers or
        b'user-agent' in headers or
        b'User-Agent' in headers
    ):
        _write_header(http_message, b'User-Agent', DEFAULT_USER_AGENT)


def _make_request_line(method, path):
    http_message = BytesIO()
    http_message.write(method)
    http_message.write(b' ')
    http_message.write(path.encode())
    http_message.write(b' ')
    http_message.write(b'HTTP/1.1\r\n')
    return http_message


def _encode_value(value):
    if isinstance(value, bytes):
        return value
    elif isinstance(value, (int, float)):
        return str(value).encode()
    return value.encode()


def _write_header(http_message, header_name, header_value):
    http_message.write(_encode_value(header_name))
    http_message.write(b': ')
    http_message.write(_encode_value(header_value))
    http_message.write(b'\r\n')


def _write_request_headers(http_message, headers, host):
    for header_name, header_value in headers.items():
        _write_header(http_message, header_name, header_value)
    _add_host(http_message, headers, host)
    _add_user_agent(http_message, headers)
    http_message.write(b'\r\n')


def _write_body(http_message, body):
    if body is None:
        return
    if not isinstance(body, bytes):
        raise RequestBodyNotBytes
    http_message.write(body)


def make_http_request_bytes(method, path, host, headers, body):
    """Construct a valid HTTP request from parameters. Not meant to be called
    outside of this library.

    :param bytes method: e.g. b'GET'
    :param str path:
    :param str host:
    :param dict headers:
    :param bytes body:
    :returns bytes: bytes of complete HTTP request
    """
    http_message = _make_request_line(method, path)
    _write_request_headers(http_message, headers, host)
    _write_body(http_message, body)
    return http_message.getvalue()
