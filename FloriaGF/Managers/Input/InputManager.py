import typing as t
from uuid import UUID, uuid4
from pathlib import Path

import glfw

from ... import Abc, Assets, Validator
from ...Core import Core
from ...AsyncEvent import AsyncEvent

from . import hints, Convert, Actions

if t.TYPE_CHECKING:
    from ... import GL

TAction = t.TypeVar(
    'TAction',
    bound=Actions.Action,
    default=Actions.actions,
    covariant=True,
)


class InputManager(
    Abc.Mixins.Repr,
    Abc.Mixins.ID[UUID],
    Abc.Mixins.Disposable,
    t.Generic[TAction],
):
    def __init__(self, window: Abc.Graphic.Windows.Window) -> None:
        super().__init__()

        self._id: UUID = uuid4()

        self._window = window

        self._handler_maps: dict[str, dict[str, dict[UUID, Actions.ActionHandler]]] = t.DefaultDict(
            lambda: t.DefaultDict(lambda: {})
        )
        self._action_maps: dict[str, dict[str, TAction]] = t.DefaultDict(lambda: {})
        self._disabled_action_maps: set[str] = set()

        glfw.set_key_callback(window.glfw_window, self._KeyCallback)

        self._on_dispose = AsyncEvent['InputManager']()

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        glfw.set_key_callback(self.window.glfw_window, None)

        self.on_dispose.Invoke(self)

    @property
    def on_dispose(self) -> AsyncEvent['InputManager']:
        return self._on_dispose

    def _Process(self):
        for map_name, map in self._action_maps.items():
            if map_name not in self._handler_maps:
                continue

            for action_name, action in map.items():
                if action_name not in self._handler_maps[map_name]:
                    continue

                for _, handler in self._handler_maps[map_name][action_name].items():
                    yield handler, action

    def _KeyCallback(self, glfw_window: 'GL.Window.GLFWWindow', key: int, scancode: int, action: int, mods: int):
        key_ = Convert.IntToKeyboardKey(key)
        stage_ = Convert.IntToPressStage(action)
        mods_ = Convert.IntToPressMods(mods)

        for handler, action_ in self._Process():
            if isinstance(handler, Actions.KeyboardHandler):
                handler.Simulate(action_, key_, stage_, mods_)

    def SetMap(self, name: str, map: dict[str, TAction], /, enable: bool = True):
        self._action_maps[name] = map
        if not enable:
            self._disabled_action_maps.add(name)

    def _MapValidate(self, map: dict[str, t.Any]) -> bool:
        return True

    async def LoadMaps(self, *pathes: str | Path, enable: bool = True):
        for path in pathes:
            asset = await Core.asset_manager.LoadFile(path, Assets.Json)
            maps = t.cast(dict[str, dict[str, t.Any]], Validator.Instance(asset.data, dict))

            for name, map in maps.items():
                if not self._MapValidate(map):
                    raise

                self.SetMap(name, map, enable=enable)

    def SetMaps(self, maps: dict[str, dict[str, TAction]], /, clear: bool = True):
        if clear:
            self.ClearMaps()

        for map_name, map in maps.items():
            self.SetMap(map_name, map)

    def SetMapStatus(self, name: str, enable: bool):
        if enable:
            if name in self._disabled_action_maps:
                self._disabled_action_maps.remove(name)

        else:
            self._disabled_action_maps.add(name)

    def RemoveMaps(self, *names: str):
        for name in names:
            self._action_maps.pop(name, None)

            if name in self._disabled_action_maps:
                self._disabled_action_maps.remove(name)

    def ClearMaps(self):
        self._action_maps.clear()
        self._disabled_action_maps.clear()

    def RegisterHandler(self, handler: Actions.ActionHandler, map: str, action: str) -> UUID:
        id = uuid4()
        self._handler_maps[map][action][id] = handler
        return id

    def GetAllHandlerRoutes(self) -> tuple[str, ...]:
        return tuple(
            f'{map_name}.{action_name} (count: {len(handlers)})'
            for map_name, map in self._handler_maps.items()
            for action_name, handlers in map.items()
        )

    def GetAllActionRoutes(self) -> tuple[str, ...]:
        return tuple(
            f'{map_name}.{action_name} {action}'
            for map_name, map in self._action_maps.items()
            for action_name, action in map.items()
        )

    def RemoveHandlers(self, ids: t.Iterable[UUID]):
        for map_name, map in self._handler_maps.items():
            for action_name, data_handlers in map.items():
                for id in (*filter(lambda id: id in ids, data_handlers.keys()),):
                    self._handler_maps[map_name][action_name].pop(id, None)

    def RemoveHandlerMaps(self, *names: str):
        for name in names:
            self._handler_maps.pop(name, None)

    def ClearHandlerMaps(self):
        self._handler_maps.clear()

    @property
    def window(self):
        return self._window

    def GetID(self):
        return self._id
