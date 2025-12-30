from OpenGL import GL
from . import hints, Convert


_depth: bool = False
_blend: bool = False


def Enable(cap: hints.capability):
    if cap == 'depth':
        global _depth

        if _depth:
            return
        _depth = True

    elif cap == 'blend':
        global _blend

        if _blend:
            return
        _blend = True

    GL.glEnable(Convert.ToOpenGLCapability(cap))


def Disable(cap: hints.capability):
    if cap == 'depth':
        global _depth

        if not _depth:
            return
        _depth = False

    elif cap == 'blend':
        global _blend

        if not _blend:
            return
        _blend = False

    else:
        GL.glDisable(Convert.ToOpenGLCapability(cap))
