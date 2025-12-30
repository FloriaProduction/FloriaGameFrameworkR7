from OpenGL import GL
import glfw
import typing as t
import types as ts
from collections import deque
from contextlib import contextmanager

from ... import Types
from .. import Binding
from .. import hints, Convert


GLFWWindow = glfw._GLFWwindow  # pyright: ignore[reportPrivateUsage]


def Create(
    size: Types.hints.size_2d,
    title: str = 'Title',
) -> GLFWWindow:
    if (
        window := glfw.create_window(
            *size,
            title,
            None,
            None,
        )
    ) is None:
        raise
    return window


def Delete(*windows: GLFWWindow):
    for window in windows:
        glfw.destroy_window(window)


def SwapBuffers(*windows: GLFWWindow):
    for window in windows:
        glfw.swap_buffers(window)


def Close(*windows: GLFWWindow):
    for window in windows:
        glfw.set_window_should_close(window, glfw.TRUE)


def SetVsync(window: GLFWWindow, value: hints.vsync) -> hints.vsync:
    with Bind(window):
        glfw.swap_interval(Convert.VSyncToInterval(value))
    return value


def ShouldClose(window: t.Optional[GLFWWindow]) -> bool:
    return window is None or glfw.window_should_close(window)


_stack = deque[GLFWWindow]()


def _Get(window: GLFWWindow):
    glfw.make_context_current(window)


def _Release(window: GLFWWindow):
    glfw.make_context_current(None)


@contextmanager
def Bind(window: GLFWWindow):
    with Binding.Bind(
        _stack,
        window,
        _Get,
        _Release,
        name='Window',
    ):
        yield
