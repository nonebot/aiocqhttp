"""
此模块提供了工具函数。
"""

import asyncio
from typing import (Any, Callable, Awaitable, Iterable, List)

from quart.utils import run_sync


def ensure_async(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """
    确保可调用对象 `func` 为异步函数，如果不是，则使用 `run_sync`
    包裹，使其在 asyncio 的默认 executor 中运行。
    """
    if asyncio.iscoroutinefunction(func):
        return func
    else:
        return run_sync(func)


def sync_wait(coro: Awaitable[Any],
              loop: asyncio.AbstractEventLoop) -> Any:
    """
    在 `loop` 中线程安全地运行 `coro`，并同步地等待其运行完成，返回运行结果。
    """
    fut = asyncio.run_coroutine_threadsafe(coro, loop)
    return fut.result()


async def run_async_funcs(funcs: Iterable[Callable[..., Awaitable[Any]]],
                          *args, **kwargs) -> List[Any]:
    """
    同时运行多个异步函数，并等待所有函数运行完成，返回运行结果列表。
    """
    results = []
    coros = []
    for f in funcs:
        coros.append(f(*args, **kwargs))
    if coros:
        results += await asyncio.gather(*coros)
    return results
