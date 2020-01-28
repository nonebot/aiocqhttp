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

    def __repr__(self):
        return f'<HttpFailed, status_code={self.status_code}>'

    def __str__(self):
        return self.__repr__()


class ActionFailed(ApiError):
    """
    Action failed to execute.

    >>> except ActionFailed as e:
    >>>     if e.retcode > 0:
    >>>         pass  # error code returned by CQHTTP
    >>>     elif e.retcode < 0:
    >>>         pass  # error code returned by CoolQ
    """

    def __init__(self, retcode):
        self.retcode = retcode

    def __repr__(self):
        return f'<ActionFailed, retcode={self.retcode}>'

    def __str__(self):
        return self.__repr__()


class NetworkError(Error, IOError):
    pass


class TimingError(Error):
    pass
