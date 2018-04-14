import json
from http.client import HTTPResponse
from io import BytesIO

from async_http import __version__

DEFAULT_USER_AGENT = 'async-http/{}'.format(__version__)

HTTP_MESSAGE = (
    '{method} {path} HTTP/1.1\r\n'
    '{headers}\r\n'
    '\r\n'
)


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



def _add_host(headers_string, headers, host):
    if not ('host' in headers or 'Host' in headers):
        if headers_string:
            headers_string += '\r\nHost: {}'.format(host)
        else:
            headers_string += 'Host: {}'.format(host)
    return headers_string


def _add_user_agent(headers_string, headers):
    if not ('user-agent' in headers or 'User-Agent' in headers):
        if headers_string:
            headers_string += '\r\nUser-Agent: {}'.format(DEFAULT_USER_AGENT)
        else:
            headers_string += 'User-Agent: {}'.format(DEFAULT_USER_AGENT)
    return headers_string


def _make_header_string(headers, host):
    # Could use a StringIO for speed here
    headers_string = '\r\n'.join(
        '{}: {}'.format(header_name, header_value)
        for header_name, header_value in headers.items()
    )
    headers_string = _add_host(headers_string, headers, host)
    headers_string = _add_user_agent(headers_string, headers)
    return headers_string


def make_http_request_string(method, path, host, headers, body):
    http_message = HTTP_MESSAGE.format(
        method=method,
        path=path,
        headers=_make_header_string(headers, host),
    )
    if body:
        http_message += body
    return http_message
