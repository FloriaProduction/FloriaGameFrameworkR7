import typing as t

from FloriaGF import Core, Abc, Computed, Config
from FloriaGF.Graphic import Window, Camera


window_cmp = Computed[Abc.Window]()


@window_cmp.GetFunc
def _():
    window_name = 'main'

    if (window := Core.window_manager.sequence.GetByNameOrDefault(window_name)) is None:
        window = Window(
            (1280, 720),
            name=window_name,
            background_color=(25, 25, 35),
        )

        window.camera = Camera(
            window,
            resolution=(1280, 720),
            projection_orthographic={
                'width': 320 * Config.PIX_scale,
                'height': 180 * Config.PIX_scale,
            },
            # projection_perspective={
            #     'fov': 80,
            # }
        )

        window = Core.window_manager.Register(window)
    return window


@window_cmp.ClearFunc
def _(value: t.Optional[Abc.Window]):
    if value is not None and not value.closed:
        value.Close()


async def Load():
    window_cmp()


async def Unload():
    window_cmp.Clear()
