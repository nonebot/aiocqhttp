"""
此模块提供了异常类。
"""

__all__ = [
    'Error',
    'ApiNotAvailable',
    'ApiError',
    'HttpFailed',
    'ActionFailed',
    'NetworkError',
    'TimingError',
]


class Error(Exception):
    """`aiocqhttp` 所有异常的基类。"""
    pass


class ApiNotAvailable(Error):
    """CQHTTP API 不可用。"""
    pass


class ApiError(Error, RuntimeError):
    """调用 CQHTTP API 发生错误。"""
    pass


class HttpFailed(ApiError):
    """HTTP 请求响应码不是 2xx。"""

    def __init__(self, status_code: int):
        self.status_code = status_code
        """HTTP 响应码。"""

    def __repr__(self):
        return f'<HttpFailed, status_code={self.status_code}>'

    def __str__(self):
        return self.__repr__()


class ActionFailed(ApiError):
    """
    CQHTTP 已收到 API 请求，但执行失败。

    ```py
    except ActionFailed as e:
        if e.retcode > 0:
            pass  # error code returned by CQHTTP
        elif e.retcode < 0:
            pass  # error code returned by CoolQ
    ```
    """

    def __init__(self, result: dict):
        self.info = result

    def __repr__(self):
        return "<ActionFailed " + ", ".join(
            f"{k}={v}" for k, v in self.info.items()) + ">"

    def __str__(self):
        return self.__repr__()


class NetworkError(Error, IOError):
    """网络错误。"""
    pass


class TimingError(Error):
    """时机错误。"""
    pass
