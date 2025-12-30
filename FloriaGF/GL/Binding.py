import typing as t
from collections import deque
from contextlib import contextmanager
import asyncio
from OpenGL import GL
import OpenGL

from . import Logger


@contextmanager
def Bind[T: t.Any](
    stack: deque[T],
    item: T,
    get_func: t.Callable[[T], t.Any],
    release_func: t.Callable[[T], t.Any],
    equal_func: t.Callable[[T, T], bool] = lambda x, y: x == y,
    name: str = '- ? -',
):
    skip = len(stack) > 0 and equal_func(stack[-1], item)

    try:
        if not skip:
            stack.append(item)
            get_func(item)

            Logger.OutPut(name, '+', True, item)

        else:
            Logger.Print(f'{name} skipped')

        yield

        if not OpenGL.ERROR_CHECKING and not skip and (code := GL.glGetError()) != GL.GL_NO_ERROR:
            raise RuntimeError(code)

    finally:
        if not skip:
            item = stack.pop()

            if len(stack) > 0:
                prev_item = stack[-1]

                get_func(prev_item)
                Logger.OutPut(name, f'* {item} -> {prev_item}', False, prev_item)

            else:
                release_func(item)
                Logger.OutPut(name, '-', False, item)
