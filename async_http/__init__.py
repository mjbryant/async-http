__version__ = '0.0.1'

__all__ = [
    'delete',
    'get',
    'head',
    'options',
    'post',
    'put',
    'init',
    'TimeoutError',
]


from async_http.api import (
    delete,
    get,
    head,
    options,
    post,
    put,
)
from async_http.api import init
from async_http.errors import TimeoutError
