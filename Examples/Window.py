import typing as t
from FloriaGF import Core, Abc, Config, Validator, AsyncEvent
from FloriaGF.Graphic import Window, Camera


_window: t.Optional[Abc.Window] = None


on_setup = AsyncEvent[Abc.Window]()
'''Вызывается после создания и регистрации каждого окна'''
on_clear = AsyncEvent[Abc.Window]()
'''Вызывается после вызова Window.Close()'''

on_load = AsyncEvent[Abc.Window]()
'''Вызывается при загрузке модуля, после инициализации окна'''
on_unload = AsyncEvent[Abc.Window]()
'''Вызывается при выгрузке модуля, перед уничтожением окна'''


def Setup():
    window = Window(
        (1280, 720),
        background_color=(25, 25, 35),
    )

    window.camera = Camera(
        window,
        resolution=window.size,
        projection_orthographic={
            'width': 320 * Config.PIX_scale,
            'height': 180 * Config.PIX_scale,
        },
        # projection_perspective={
        #     'fov': 80,
        # }
    )

    Core.window_manager.Register(window)

    @window.on_closed
    def _(window: Abc.Window):
        Core.window_manager.RemoveClosedWindows(True)

    on_setup.Invoke(window)

    return window


def Clear(window: Abc.Window):
    window.Close()
    on_clear.Invoke(window)


def Get():
    return Validator.NotNone(_window, error='Window is not initialized')


def GetOrDefault[TDefault: t.Optional[t.Any]](default: TDefault = None) -> Abc.Window | TDefault:
    if _window is None:
        return default
    return _window


async def Load():
    global _window

    if _window is not None:
        raise

    _window = Setup()
    on_load.Invoke(_window)


async def Unload():
    global _window

    if _window is None:
        return

    Clear(_window)
    on_unload.Invoke(_window)

    _window = None


async def Reload():
    await Unload()
    await Load()
