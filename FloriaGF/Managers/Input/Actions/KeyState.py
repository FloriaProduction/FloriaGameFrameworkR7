import typing as t

from .Base import Action, KeyboardHandler

if t.TYPE_CHECKING:
    from ....AsyncEvent import AsyncEvent
    from .. import hints
    from ..InputManager import InputManager


class KeyStateAction(Action, t.TypedDict):
    key: 'hints.key | t.Iterable[hints.key]'


def ValidateKeyStateAction(action: Action):
    if 'key' not in action:
        return False


class KeyStateHandler(
    KeyboardHandler['AsyncEvent[bool]'],
):
    def __init__(self, input_manager: 'InputManager', map: str, action: str, *args: t.Any, **kwargs: t.Any):
        super().__init__(input_manager, map, action, *args, **kwargs)

        self.is_pressed: bool = False

    def Simulate(
        self,
        action: KeyStateAction,
        key: 'hints.key',
        stage: 'hints.press_stage',
        mods: 'set[hints.press_mod]',
        *args: t.Any,
        **kwargs: t.Any,
    ) -> t.Any:
        if action['type'] != 'state':
            return

        action_keys = set((keys_,)) if isinstance(keys_ := action['key'], str) else set(keys_)

        if key not in action_keys:
            return

        if stage == 'press':
            self.is_pressed = True

        elif stage == 'release':
            self.is_pressed = False

        if stage != 'repeat':
            self.event.Invoke(self.is_pressed)
