# async-http
Blocking interface for python HTTP calls using asyncio.

Works by running `asyncio`'s [event loop](https://docs.python.org/3/library/asyncio-eventloops.html#event-loops) in a separate thread and sending I/O work to it, similar to how the awesome [crochet](https://github.com/itamarst/crochet) library does with Twisted's reactor.

## Usage
```python
>>> import aio
>>> future = aio.get('http://www.google.com')
>>> response = future.result()
```

## Parallelism!
You can see parallel speedups when comparing with `requests`, run in serial:

```python
def test(n=20):
    start = time.time()
    for _ in range(n):
        requests.get('http://www.google.com')
    print(time.time() - start)
    
def test_async(n=20):
    start = time.time()
    futures = [aio.get('http://www.google.com') for _ in range(n)]
    results = [f.result() for f in futures]
    print(time.time() - start)
```

The `test` function's timing grows linearly with `n`, while `test_async` does not.
