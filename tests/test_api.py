from unittest import TestCase

import pytest

# Incidentally test that 'import *' works
from async_http import *
from async_http.http_utils import DEFAULT_USER_AGENT
from tests.server import DEFAULT_TEST_HOST
from tests.server import DEFAULT_TEST_IP
from tests.server import DEFAULT_TEST_PORT
from tests.server import DEFAULT_TEST_URL
from tests.server import SLEEP_HEADER


@pytest.mark.usefixtures("run_server")
class ServerTest(TestCase):
    pass


class TestBasicApi(ServerTest):

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
        request_body = 'This is my body'
        response = get(DEFAULT_TEST_URL, body=request_body).result()

        assert response.status_code == 200
        assert response.json()['body_length'] == len(request_body)

    def test_timeout(self):
        sleep_time = 1
        headers = {SLEEP_HEADER: sleep_time}
        with pytest.raises(TimeoutError):
            get(DEFAULT_TEST_URL, headers=headers).result(timeout=sleep_time/2)
