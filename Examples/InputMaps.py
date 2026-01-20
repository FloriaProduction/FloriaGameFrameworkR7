import typing as t

from FloriaGF.Managers.Input import InputManager, Actions

from . import Input


@Input.on_setup
async def _(im: InputManager):
    im.SetMaps({
        'core': {
            'exit': {
                'type': 'press',
                'key': 'f10',
                'stages': 'press',
            },
        },
    })

    @Actions.PressHandler(im, 'core', 'exit').event
    def _(*args: t.Any):
        from FloriaGF import Core

        Core.Stop()