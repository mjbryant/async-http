HTTP_MESSAGE = (
    '{method} {path} HTTP/1.1\r\n'
    '{headers}\r\n'
    '\r\n'
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
            headers_string += '\r\nUser-Agent: async-http'
        else:
            headers_string += 'User-Agent: async-http'
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
