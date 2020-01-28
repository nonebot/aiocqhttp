import asyncio
from contextvars import copy_context
from functools import partial, wraps
from inspect import isgenerator
from typing import (Any, Callable, Coroutine, Generator, AsyncGenerator,
                    Awaitable)


def run_sync(func: Callable[..., Any]) -> Callable[
    ..., Coroutine[Any, None, None]]:
    """Ensure that the sync function is run within the event loop.

    If the *func* is not a coroutine it will be wrapped such that
    it runs in the default executor (use loop.set_default_executor
    to change). This ensures that synchronous functions do not
    block the event loop.

    This function and run_sync_iterable are copied from Quart:
    https://gitlab.com/pgjones/quart/blob/dfb02bb54b6ad1c92011d7a1fb91daadaa3cf243/src/quart/utils.py
    """

    @wraps(func)
    async def _wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, copy_context().run, partial(func, *args, **kwargs)
        )
        if isgenerator(result):
            return run_sync_iterable(result)
        else:
            return result

    _wrapper._quart_async_wrapper = True
    return _wrapper


def run_sync_iterable(
        iterable: Generator[Any, None, None]) -> AsyncGenerator[Any, None]:
    async def _gen_wrapper() -> AsyncGenerator[Any, None]:
        # Wrap the generator such that each iteration runs
        # in the executor. Then rationalise the raised
        # errors so that it ends.
        def _inner() -> Any:
            # https://bugs.python.org/issue26221
            # StopIteration errors are swallowed by the
            # run_in_exector method
            try:
                return next(iterable)
            except StopIteration:
                raise StopAsyncIteration()

        loop = asyncio.get_running_loop()
        while True:
            try:
                yield await loop.run_in_executor(None, copy_context().run,
                                                 _inner)
            except StopAsyncIteration:
                return

    return _gen_wrapper()


def ensure_async(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    if asyncio.iscoroutinefunction(func):
        return func
    else:
        return run_sync(func)


def sync_wait(coro: Awaitable[Any],
              loop: asyncio.AbstractEventLoop) -> Any:
    fut = asyncio.run_coroutine_threadsafe(coro, loop)
    return fut.result()
