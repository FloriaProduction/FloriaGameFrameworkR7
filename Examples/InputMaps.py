import typing as t

from FloriaGF.Managers.Input import InputManager, Actions

from . import Window, Input


@Input.on_setup
async def _(im: InputManager):
    im.SetMaps(
        {
            'core': {
                'exit': {
                    'type': 'press',
                    'key': 'f10',
                    'stages': 'press',
                },
            },
            'camera': {
                'zoom_in': {
                    'type': 'press',
                    'key': 'up',
                    'stages': ('press', 'repeat'),
                },
                'zoom_out': {
                    'type': 'press',
                    'key': 'down',
                    'stages': ('press', 'repeat'),
                },
            }
        }
    )

    @Actions.KeyPressHandler(im, 'core', 'exit').event
    def _(*args: t.Any):
        from FloriaGF import Core

        Core.Stop()
    
    @Actions.KeyPressHandler(im, 'camera', 'zoom_in').event
    def _(*args: t.Any):
        (camera := Window.Get().camera).SetScale(camera.scale - 0.25, min_value=0.00001)
    
    
    @Actions.KeyPressHandler(im, 'camera', 'zoom_out').event
    def _(*args: t.Any):
        (camera := Window.Get().camera).SetScale(camera.scale + 0.25, max_value=10)
