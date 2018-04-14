from unittest import TestCase

# Incidentally test that 'import *' works
from async_http import *
from async_http.http_utils import DEFAULT_USER_AGENT
from async_http.http_utils import parse_http_response
from tests.server import run_server_in_thread
from tests.server import DEFAULT_TEST_HOST
from tests.server import DEFAULT_TEST_IP
from tests.server import DEFAULT_TEST_PORT
from tests.server import DEFAULT_TEST_URL


class TestGet(TestCase):

    @classmethod
    def setup_class(cls):
        run_server_in_thread()

    @staticmethod
    def _assert_empty_200(response):
        assert response.status_code == 200
        assert response.json() == {
            'body_length': 0,  # No request body
            'method': 'GET',
        }

    def test_get(self):
        headers = {'Host': 'abcd', 'User-Agent': 'fakedit'}
        future = get(DEFAULT_TEST_URL, headers=headers)
        response = parse_http_response(future.result())

        self._assert_empty_200(response)

        assert response.headers['X-Host'] == headers['Host']
        assert response.headers['X-User-Agent'] == headers['User-Agent']

    def test_get_using_ip(self):
        future = get('http://{}:{}'.format(
            DEFAULT_TEST_IP,
            DEFAULT_TEST_PORT,
        ))
        response = parse_http_response(future.result())

        self._assert_empty_200(response)

    def test_get_default_headers(self):
        future = get(DEFAULT_TEST_URL)
        response = parse_http_response(future.result())

        self._assert_empty_200(response)

        assert response.headers['X-Host'] == DEFAULT_TEST_HOST
        assert response.headers['X-User-Agent'] == DEFAULT_USER_AGENT

    def test_get_with_body(self):
        request_body = 'This is my body'
        future = get(DEFAULT_TEST_URL, body=request_body)
        response = parse_http_response(future.result())

        assert response.status_code == 200
        assert response.json()['body_length'] == len(request_body)
