import mock
from unittest import TestCase
from http.client import RemoteDisconnected

import pytest
from aiodns.error import DNSError

# Incidentally test that 'import *' works
from async_http import *
from async_http.errors import RequestBodyNotBytes
from async_http.errors import TimeoutError
from async_http.http_utils import DEFAULT_USER_AGENT
from tests.server import CLOSE_CONNECTION_HEADER
from tests.server import DEFAULT_TEST_HOST
from tests.server import DEFAULT_TEST_IP
from tests.server import DEFAULT_TEST_PORT
from tests.server import DEFAULT_TEST_URL
from tests.server import SEND_ERROR_HEADER
from tests.server import SLEEP_HEADER


@pytest.mark.usefixtures("run_server")
class ServerTest(TestCase):
    pass


class TestBasicApi(ServerTest):
    """Test all basic API functionality, using only the GET method."""

    @staticmethod
    def _assert_empty_200(response):
        assert response.status_code == 200
        assert response.json() == {
            'body_length': 0,  # No request body
            'method': 'GET',
        }

    def test_get(self):
        headers = {'Host': 'abcd', 'User-Agent': 'fakedit'}
        response = get(DEFAULT_TEST_URL, headers=headers).result()

        self._assert_empty_200(response)

        assert response.headers['X-Host'] == headers['Host']
        assert response.headers['X-User-Agent'] == headers['User-Agent']

    def test_get_using_ip(self):
        response = get('http://{}:{}'.format(
            DEFAULT_TEST_IP,
            DEFAULT_TEST_PORT,
        )).result()

        self._assert_empty_200(response)

    def test_get_default_headers(self):
        response = get(DEFAULT_TEST_URL).result()

        self._assert_empty_200(response)

        assert response.headers['X-Host'] == DEFAULT_TEST_HOST
        assert response.headers['X-User-Agent'] == DEFAULT_USER_AGENT

    def test_get_with_body(self):
        request_body = b'This is my body'
        response = get(DEFAULT_TEST_URL, body=request_body).result()

        assert response.status_code == 200
        assert response.json()['body_length'] == len(request_body)

    @pytest.mark.skip("Doesn't work on CI servers")
    def test_error_code(self):
        headers = {SEND_ERROR_HEADER: 500}
        response = get(DEFAULT_TEST_URL, headers=headers).result()

        assert response.status_code == 500
        assert 'Internal Server Error' in response.body.decode()

    def test_header_encoding(self):
        # Make sure headers of various values are properly encoded
        host_header = 'somehost'
        user_agent_header = b'whatever'
        int_header = 123
        float_header = 123.5
        headers = {
            b'Host': host_header,
            'User-Agent': user_agent_header,
            'X-My-Int': int_header,
            'X-My-Float': float_header,
        }
        response = get(DEFAULT_TEST_URL, headers=headers).result()

        self._assert_empty_200(response)

        response.headers.pop('Server')
        response.headers.pop('Date')
        assert response.headers == {
            'X-Host': host_header,
            'X-User-Agent': user_agent_header.decode(),
            'X-X-My-Int': str(int_header),
            'X-X-My-Float': str(float_header),
            'Content-Type': 'application/json',
        }


class TestHTTPMethods(ServerTest):

    def _assert_200(self, api_function, expected_method):
        result = api_function(DEFAULT_TEST_URL).result()
        assert result.status_code == 200
        assert result.json()['method'] == expected_method

    def test_api_methods(self):
        for function, method in [
            (delete, 'DELETE'),
            (get, 'GET'),
            (head, 'HEAD'),
            (options, 'OPTIONS'),
            (post, 'POST'),
            (put, 'PUT'),
        ]:
            self._assert_200(function, method)


class TestErrors(ServerTest):

    def test_server_closes_connection(self):
        headers = {CLOSE_CONNECTION_HEADER: 1}
        with pytest.raises(RemoteDisconnected):
            get(DEFAULT_TEST_URL, headers=headers).result()

    def test_dns_resolution_error(self):
        with pytest.raises(DNSError):
            with mock.patch('async_http.api._resolve_dns', side_effect=DNSError):
                get('http://fdjkldsjkljfkelwjfkljsdklfjksldakjlf').result()

    def test_server_isnt_running(self):
        with pytest.raises(ConnectionRefusedError):
            # Use an unlikely port. This is a dumb test but it still seems
            # better to have it than to not, to affirm the error API.
            get('http://127.0.0.1:13808').result()

    def test_timeout(self):
        sleep_time = 1
        headers = {SLEEP_HEADER: sleep_time}
        with pytest.raises(TimeoutError):
            get(DEFAULT_TEST_URL, headers=headers).result(timeout=sleep_time/2)

    def test_request_body_not_bytes(self):
        with pytest.raises(RequestBodyNotBytes):
            get(DEFAULT_TEST_URL, body='my body').result()
