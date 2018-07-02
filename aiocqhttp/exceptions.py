class Error(Exception):
    pass


class ApiNotAvailable(Error):
    pass


class ApiError(Error, RuntimeError):
    pass


class HttpFailed(ApiError):
    """HTTP status code is not 2xx."""

    def __init__(self, status_code):
        self.status_code = status_code


class ActionFailed(ApiError):
    """
    Action failed to execute.

    >>> except ActionFailed as e:
    >>>     if e.retcode > 0:
    >>>         pass  # error code returned by HTTP API
    >>>     elif e.retcode < 0:
    >>>         pass  # error code returned by CoolQ
    """

    def __init__(self, retcode):
        self.retcode = retcode


class NetworkError(Error, IOError):
    pass
