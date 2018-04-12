from setuptools import setup

from async_http import __version__


setup(
    name='async-http',
    version=__version__,
    description='Synchronous interface to making asynchronous HTTP requests',
    author='Michael Bryant',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=[
        'async_http',
    ],
    install_requires=[
        'aiodns',
    ],
    extras_require={
        'test': ['pytest'],
    },
)
