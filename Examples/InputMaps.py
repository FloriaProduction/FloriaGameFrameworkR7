import typing as t

from FloriaGF.Managers.Input import InputManager, Actions

from . import Input


@Input.on_setup
async def _(im: InputManager):
    await im.LoadMaps(
        # './Data/InputMaps/core.json',
        './Data/InputMaps/camera.json',
    )

    im.SetMap(
        'core',
        {
            'exit': {
                'type': 'press',
                'key': 'f10',
                'stages': 'press',
            },
            'reload_window': {
                'type': 'press',
                'key': 'f8',
                'mods': 'shift',
                'stages': 'release',
            },
            'all_handler_routes': {
                'type': 'press',
                'key': 'f7',
                'stages': 'press',
            },
        },
    )

    @Actions.PressHandler(im, 'core', 'exit').event
    def _(*args: t.Any):
        from FloriaGF import Core

        Core.Stop()

    @Actions.PressHandler(im, 'core', 'reload_window').event
    async def _(*args: t.Any):
        from . import Window

        await Window.Reload()

    @Actions.PressHandler(im, 'core', 'all_handler_routes').event
    def _(*args: t.Any):
        print(
            f'{im} has:\nHandler routes:\n{'\n'.join(map(lambda x: f'- {x}', im.GetAllHandlerRoutes()))}\nAction routes:\n{'\n'.join(map(lambda x: f'- {x}', im.GetAllActionRoutes()))}'
        )
