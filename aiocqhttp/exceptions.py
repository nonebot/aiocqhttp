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
    """OneBot API 不可用。"""
    pass


class ApiError(Error, RuntimeError):
    """调用 OneBot API 发生错误。"""
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
    OneBot 已收到 API 请求，但执行失败。

    ```py
    except ActionFailed as e:
        print(e)
        # 或检查返回码
        if e.retcode == 12345:
            pass
    ```
    """

    def __init__(self, result: dict):
        self.result = result

    @property
    def retcode(self) -> int:
        """OneBot API 请求的返回码。"""
        return self.result['retcode']

    def __repr__(self):
        return "<ActionFailed " + ", ".join(
            f"{k}={repr(v)}" for k, v in self.result.items()) + ">"

    def __str__(self):
        return self.__repr__()


class NetworkError(Error, IOError):
    """网络错误。"""
    pass


class TimingError(Error):
    """时机错误。"""
    pass
