import pytest

from tests.server import run_server_in_thread


@pytest.fixture(scope="module")
def run_server():
    run_server_in_thread()
