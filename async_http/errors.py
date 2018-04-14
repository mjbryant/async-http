class TimeoutError(Exception):
    """Error raised when .result() on a future doesn't return within time."""
