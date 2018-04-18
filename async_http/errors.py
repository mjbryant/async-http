class TimeoutError(Exception):
    """Error raised when .result() on a future doesn't return within time."""


class EventLoopNotInitialized(Exception):
    """Event loop not initialized."""


class RequestBodyNotBytes(Exception):
    """Request body must be bytes."""
