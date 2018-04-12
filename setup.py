from setuptools import find_packages
from setuptools import setup

from async_http import __version__


setup(
    name='async-http',
    version=__version__,
    description='Synchronous interface to making asynchronous HTTP requests',
)
