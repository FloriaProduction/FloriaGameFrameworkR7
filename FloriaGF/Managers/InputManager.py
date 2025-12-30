import typing as t
from abc import ABC, abstractmethod
from enum import StrEnum
import glfw
from collections import deque
from time import perf_counter
import math

from .. import Abc, Utils, Convert
from ..TimeoutScheduler import TimeoutScheduler
from ..AsyncEvent import AsyncEvent
from ..Types.Vec import Vec2
from ..Types.Angle import Angle2D
from ..Types.Direction import Direction
from ..Core import Core
from ..Loggers import input_manager_logger


class Key(t.NamedTuple):
    key: int
    action: int
    mod: t.Optional[int] = None


action_type = t.Literal[
    'click',
    'double',
    'vec2',
    'hold',
    'scroll',
]

press_stage = t.Literal[
    'press',
    'repeat',
    'release',
]

press_mod = t.Optional[
    t.Literal[
        'shift',
        'ctrl',
        'alt',
        'capslock',
        'numlock',
    ]
]


class Action(t.TypedDict):
    type: action_type


class ActionData[
    TAction: Action,
    TEvent: AsyncEvent[...],
](
    ABC,
):
    def __init__(self, action: TAction) -> None:
        self.action: TAction = action

    @property
    def type(self) -> action_type:
        return self.action['type']

    @abstractmethod
    def Processing(self, event: TEvent, *args: t.Any, **kwargs: t.Any) -> t.Any: ...


class KeyActionData[
    TAction: Action,
    TEvent: AsyncEvent[...],
](
    ActionData[TAction, TEvent],
):
    @abstractmethod
    def Processing(self, event: TEvent, key: Key) -> t.Any: ...

    @staticmethod
    def KeyActionToStage(action: int) -> press_stage:
        match action:
            case glfw.PRESS:
                return 'press'
            case glfw.REPEAT:
                return 'repeat'
            case glfw.RELEASE:
                return 'release'
            case _:
                raise RuntimeError()

    @staticmethod
    def KeyModToMods(mods: t.Optional[int]) -> t.Optional[press_mod]:
        if mods is None:
            return None
        match mods:
            case glfw.MOD_SHIFT:
                return 'shift'

            case glfw.MOD_ALT:
                return 'alt'

            case glfw.MOD_CAPS_LOCK:
                return 'capslock'

            case glfw.MOD_CONTROL:
                return 'ctrl'

            case glfw.MOD_NUM_LOCK:
                return 'numlock'

            case _:
                raise RuntimeError()


class ScrollActionData[
    TAction: Action,
    TEvent: AsyncEvent[...],
](
    ActionData[TAction, TEvent],
):
    @abstractmethod
    def Processing(self, event: TEvent, offset: Vec2[float]) -> t.Any: ...


class ActionClick(
    Action,
):
    key: int | t.Collection[int]
    mods: t.NotRequired[t.Sequence[press_mod] | press_mod]
    stages: t.NotRequired[t.Sequence[press_stage] | press_stage]


class ActionClickData(
    KeyActionData[ActionClick, AsyncEvent[press_stage, press_mod]],
):
    def __init__(self, action: ActionClick) -> None:
        super().__init__(action)

        self.sch_id: t.Optional[int] = None

    def Processing(
        self,
        event: AsyncEvent[press_stage, press_mod],
        key: Key,
    ):
        action_key = self.action['key']

        if key.key not in (action_key if isinstance(action_key, t.Collection) else (action_key,)):
            return

        stage = self.KeyActionToStage(key.action)
        mod = self.KeyModToMods(key.mod)

        if (
            (stages := self.action.get('stages')) is not None
            and (stage != stages if isinstance(stages, str) else stage not in stages)
        ) or ((mods := self.action.get('mods')) is not None and (mod != mods if isinstance(mods, str) else mod not in mods)):
            return

        event.Invoke(stage, mod)


class ActionDoubleClick(
    Action,
):
    key: int | t.Collection[int]
    mods: t.NotRequired[t.Sequence[press_mod] | press_mod]
    delay: t.NotRequired[float]


class ActionDoubleClickData(
    KeyActionData[ActionDoubleClick, AsyncEvent[...]],
):
    def __init__(self, action: ActionDoubleClick) -> None:
        super().__init__(action)

        self.last: float = perf_counter()

    def Processing(
        self,
        event: AsyncEvent[...],
        key: Key,
    ):
        stage = self.KeyActionToStage(key.action)
        mod = self.KeyModToMods(key.mod)

        action_key = self.action['key']

        if (
            key.key not in (action_key if isinstance(action_key, t.Collection) else (action_key,))
            or stage != 'press'
            or ((mods := self.action.get('mods')) is not None and (mod != mods if isinstance(mods, str) else mod not in mods))
        ):
            return

        now = perf_counter()
        if (now - self.last) < self.action.get('delay', 0.3):
            event.Invoke()

        self.last = now


class ActionVector2D(
    Action,
):
    mods: t.NotRequired[t.Sequence[press_mod] | press_mod]
    up: int | t.Collection[int]
    left: int | t.Collection[int]
    down: int | t.Collection[int]
    right: int | t.Collection[int]


class ActionVector2DData(
    KeyActionData[ActionVector2D, AsyncEvent[Angle2D]],
):
    def __init__(self, action: ActionVector2D) -> None:
        super().__init__(action)

        self.direction = Direction()
        self.angle: t.Optional[float] = None

    def Processing(
        self,
        event: AsyncEvent[Angle2D],
        key: Key,
    ):
        stage = self.KeyActionToStage(key.action)
        mod = self.KeyModToMods(key.mod)

        if stage not in ['press', 'release'] or (
            stage == 'press'
            and (mods := self.action.get('mods')) is not None
            and (mod != mods if isinstance(mods, str) else mod not in mods)
        ):
            return

        is_press = stage == 'press'
        direction: dict[t.Literal['up', 'left', 'down', 'right'], bool] = {
            'up': False,
            'left': False,
            'down': False,
            'right': False,
        }
        for direct in direction.keys():
            action_key = self.action[direct]
            if len(keys := (action_key if isinstance(action_key, t.Collection) else (action_key,))) > 0 and key.key in keys:
                direction[direct] = is_press

        self.direction = Direction(**direction)

        event.Invoke(self.direction.angle)


class ActionHold(
    Action,
):
    key: int
    delay: t.NotRequired[float]
    mods: t.NotRequired[t.Sequence[press_mod] | press_mod]
    stages: t.NotRequired[t.Sequence[press_stage] | press_stage]


class ActionHoldData(
    KeyActionData[ActionHold, AsyncEvent[press_stage]],
):
    def __init__(self, action: ActionHold) -> None:
        super().__init__(action)

        self.sch_id: t.Optional[int] = None

    def Processing(
        self,
        event: AsyncEvent[press_stage],
        key: Key,
    ):
        if key.key != self.action['key']:
            return

        stage = self.KeyActionToStage(key.action)
        stages = self.action.get('stages')

        if stage == 'press':
            if self.sch_id is None:
                callable_event = event if stages is None or 'repeat' in stages else None

                async def InvokeEvent():
                    if callable_event is not None:
                        callable_event.Invoke('repeat')

                self.sch_id = Core.scheduler.SetTimeout(
                    self.action.get('delay', 0.3),
                    InvokeEvent,
                )

                if stages is None or 'press' in stages:
                    event.Invoke('press')

        elif stage == 'release':
            if self.sch_id is not None:
                Core.scheduler.Cancel(self.sch_id)

                self.sch_id = None
                if stages is None or 'release' in stages:
                    event.Invoke('release')


class ActionScroll(
    Action,
):
    pass


class ActionScrollData(
    ScrollActionData[ActionScroll, AsyncEvent[Vec2[float]]],
):
    def Processing(
        self,
        event: AsyncEvent[Vec2[float]],
        offset: Vec2[float],
    ):
        event.Invoke(offset)


actions = t.Union[
    ActionClick,
    ActionDoubleClick,
    ActionVector2D,
    ActionHold,
    ActionScroll,
]


class InputManager(Abc.Mixins.Disposable):
    def __init__(self, window: Abc.Graphic.Windows.Window) -> None:
        super().__init__()

        self._window = window

        self._maps: dict[str, dict[str, dict[action_type, ActionData[Action, AsyncEvent[...]]]]] = {}
        self._event_maps: dict[str, dict[str, dict[t.Optional[action_type], AsyncEvent[...]]]] = {}
        self._disabled_maps: set[str] = set()

        glfw.set_key_callback(window.glfw_window, self._KeyCallback)
        glfw.set_mouse_button_callback(window.glfw_window, self._MouseCallback)
        self._key_pool = deque[Key]()

        glfw.set_cursor_pos_callback(window.glfw_window, self._CursorPosCallback)
        self._cursor_pos_pool = deque[Vec2[float]]()
        self._cursor_pos_event = AsyncEvent[Vec2[float]]()

        glfw.set_scroll_callback(window.glfw_window, self._ScrollCallback)
        self._scroll_pool = deque[Vec2[float]]()

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        pass
        # return super().Delete()

    def SetMap(self, name: str, map: dict[str, actions], /, enable: bool = True):
        if name not in self._maps:
            self._maps[name] = {}

        for action_name, action in map.items():
            if action_name not in self._maps[name]:
                self._maps[name][action_name] = {}

            match action['type']:
                case 'click':
                    cls = ActionClickData

                case 'double':
                    cls = ActionDoubleClickData

                case 'vec2':
                    cls = ActionVector2DData

                case 'hold':
                    cls = ActionHoldData

                case 'scroll':
                    cls = ActionScrollData

                case _:
                    raise RuntimeError()

            self._maps[name][action_name][action['type']] = cls(action)  # pyright: ignore[reportArgumentType]

        if not enable:
            self.DisableMap(name)

    def SetMaps(self, maps: dict[str, dict[str, actions]]):
        self._maps.clear()
        for map_name, map in maps.items():
            self.SetMap(map_name, map)

    def EnabledMap(self, name: str):
        if name in self._disabled_maps:
            self._disabled_maps.remove(name)

    def DisableMap(self, name: str):
        if name not in self._maps:
            raise ValueError()
        self._disabled_maps.add(name)

    def _KeyCallback(self, glfw_window: t.Any, key: int, scancode: int, action: int, mods: int):
        self._key_pool.append(Key(key, action, mods if mods != 0 else None))

    def _MouseCallback(self, glfw_window: t.Any, button: int, action: int, mods: int):
        self._key_pool.append(Key(button, action, mods if mods != 0 else None))

    def _CursorPosCallback(self, glfw_window: t.Any, x: float, y: float):
        self._cursor_pos_pool.append(Vec2[float](x, y))

    def _ScrollCallback(self, glfw_window: t.Any, x_offset: float, y_offset: float):
        self._scroll_pool.append(Vec2[float](x_offset, y_offset))

    def Simulate(self):
        def SimulateItem(action_data: t.Type[ActionData[Action, AsyncEvent[...]]], *args: t.Any):
            for map_name, map in self._maps.items():
                if map_name in self._disabled_maps or (event_map := self._event_maps.get(map_name)) is None:
                    continue

                for action_name, types_action in map.items():
                    if (types_event := event_map.get(action_name)) is None:
                        continue

                    for data in types_action.values():
                        if (event := types_event.get(data.type)) is not None and isinstance(data, action_data):
                            data.Processing(event, *args)

        while len(self._key_pool) > 0:
            SimulateItem(KeyActionData, self._key_pool.pop())

        while len(self._scroll_pool) > 0:
            SimulateItem(ScrollActionData, self._scroll_pool.pop())

    def GetActionEvent(self, map: str, action: str, type: t.Optional[action_type] = None) -> AsyncEvent[...]:
        if map not in self._event_maps:
            self._event_maps[map] = {}
        if action not in self._event_maps[map]:
            self._event_maps[map][action] = {}
        if type not in self._event_maps[map][action]:
            self._event_maps[map][action][type] = AsyncEvent()
        return self._event_maps[map][action][type]

    def GetClick(self, map: str, action: str):
        return t.cast(AsyncEvent[press_stage, press_mod], self.GetActionEvent(map, action, 'click'))

    def GetDoubleClick(self, map: str, action: str):
        return self.GetActionEvent(map, action, 'double')

    def GetVector2D(self, map: str, action: str):
        return t.cast(AsyncEvent[Angle2D], self.GetActionEvent(map, action, 'vec2'))

    def GetHold(self, map: str, action: str):
        return t.cast(AsyncEvent[press_stage], self.GetActionEvent(map, action, 'hold'))

    def GetCursorPos(self):
        return self._cursor_pos_event

    def GetScroll(self, map: str, action: str):
        return t.cast(AsyncEvent[Vec2[float]], self.GetActionEvent(map, action, 'scroll'))

    @property
    def window(self):
        return self._window
