import typing as t
from OpenGL import GL

from . import hints, Convert
from .Window.Common import GLFWWindow


capabilities: dict[int, dict[str, bool]] = t.DefaultDict(lambda: {})


def Enable(window: GLFWWindow, cap: hints.capability):
    window_id = id(window)

    if capabilities[window_id].get(cap, False) is True:
        return
    capabilities[window_id][cap] = True

    GL.glEnable(Convert.ToOpenGLCapability(cap))


def Disable(window: GLFWWindow, cap: hints.capability):
    window_id = id(window)

    if capabilities[window_id].get(cap, False) is False:
        return
    capabilities[window_id][cap] = False

    GL.glDisable(Convert.ToOpenGLCapability(cap))
