import typing as t
from FloriaGF import Core, Abc, Validator, AsyncEvent
from FloriaGF.Graphic import Window, Camera


on_setup = AsyncEvent[Abc.Window]()
on_clear = AsyncEvent[Abc.Window]()

on_load = AsyncEvent[Abc.Window]()
on_unload = AsyncEvent[Abc.Window]()


_window: t.Optional[Abc.Window] = None


def Get():
    return Validator.NotNone(_window, error='Window is not initialized')


def GetOrDefault[TDefault: t.Optional[t.Any]](default: TDefault = None) -> Abc.Window | TDefault:
    if _window is None:
        return default
    return _window


def Setup():
    window = Window(
        (1280, 720),
        background_color=(25, 25, 35),
    )

    window.camera = Camera(
        window,
        resolution=(320, 180),
    )

    Core.window_manager.Register(window)

    on_setup.Invoke(window)

    return window


def Clear(window: Abc.Window):
    window.Close()
    on_clear.Invoke(window)


async def Load():
    global _window

    if _window is not None:
        raise

    _window = Setup()
    await on_load.InvokeAsync(_window)


async def Unload():
    global _window

    if _window is None:
        return

    Clear(_window)
    await on_unload.InvokeAsync(_window)

    _window = None

async def Reload():
    await Unload()
    await Load()
