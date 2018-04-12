"""
For example:
    >> future = get('/', host='127.0.0.1', port=5000)
    >> response = future.result()

This will also try to resolve DNS, so this should work:
    >> future = get('/', host='www.google.com', port=80)
    >> response = future.result()
"""
import asyncio
import ipaddress
import socket
from threading import Thread
from urllib.parse import urlparse

import aiodns

from http_utils import make_http_request_string
from protocol import Future
from protocol import Protocol


_LOOP = None
_AIO_INITIALIZED = False

_SLEEP_TIME = 0.005


class EventLoopNotInitialized(Exception):
    """Event loop not initialized."""


def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def init():
    global _AIO_INITIALIZED
    if _AIO_INITIALIZED:
        return

    global _LOOP
    _LOOP = asyncio.get_event_loop()
    t = Thread(target=_start_background_loop, args=(_LOOP,))
    t.setDaemon(True)
    t.start()

    _AIO_INITIALIZED = True


async def resolve_dns(hostname):
    return await aiodns.DNSResolver(loop=_LOOP).gethostbyname(
        hostname,
        socket.AF_INET,
    )


async def _make_request_async(host, port, http_content):
    """Main asynchronous entry point. Optionally resolves DNS, then opens a TCP
    connection and makes a request.
    """
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        dns_result = await resolve_dns(host)
        host = dns_result.addresses[0]

    _, protocol = await _LOOP.create_connection(
        lambda: Protocol(http_content),
        host,
        port,
    )
    while True:
        if not protocol.finished:
            await asyncio.sleep(_SLEEP_TIME)
        else:
            return protocol.response


def _make_request(host, port, http_content):
    """Connects via TCP to host:port and immediately sends http_content. The
    connection is managed by a coroutine run on a background thread.

    :param str host: IPv4 or hostname; if latter, hostname is resolved
    :param int port:
    :param str http_content: full HTTP body to send
    :returns asyncio.Future:
    """
    if not _AIO_INITIALIZED:
        raise EventLoopNotInitialized()
    return asyncio.run_coroutine_threadsafe(
        _make_request_async(host, port, http_content),
        _LOOP,
    )


def _get_port(parsed_url):
    port = parsed_url.port
    if port is None:
        port = 80 if parsed_url.scheme == 'http' else 443
    return port


def _get_path(parsed_url):
    return parsed_url.path or '/'


def _request(method, url, headers, body):
    parsed_url = urlparse(url)
    return _make_request(
        host=parsed_url.hostname,
        port=_get_port(parsed_url),
        http_content=make_http_request_string(
            method=method,
            path=_get_path(parsed_url),
            host=parsed_url.hostname,
            headers=headers,
            body=body,
        ),
    )


def get(url, headers={}, body={}):
    return Future(_request('GET', url, headers, body))


def put(url, headers={}, body={}):
    return Future(_request('PUT', url, headers, body))


def post(url, headers={}, body={}):
    return Future(_request('POST', url, headers, body))


def delete(url, headers={}, body={}):
    return Future(_request('DELETE', url, headers, body))


def head(url, headers={}, body={}):
    return Future(_request('HEAD', url, headers, body))


def options(url, headers={}, body={}):
    return Future(_request('OPTIONS', url, headers, body))