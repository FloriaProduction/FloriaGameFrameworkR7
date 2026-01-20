import typing as t

from .Base import Action, KeyboardHandler

if t.TYPE_CHECKING:
    from ....AsyncEvent import AsyncEvent
    from .. import hints


class KeyPressAction(Action, t.TypedDict):
    key: 'hints.key | t.Iterable[hints.key]'
    mods: 't.NotRequired[t.Optional[hints.press_mod | t.Iterable[hints.press_mod]]]'
    stages: 't.NotRequired[t.Optional[hints.press_stage | t.Sequence[hints.press_stage]]]'


def ValidateKeyPressAction(action: Action):
    if 'key' not in action:
        return False


class KeyPressHandler(
    KeyboardHandler['AsyncEvent[hints.key,hints.press_stage,set[hints.press_mod]]'],
):
    def Simulate(
        self,
        action: KeyPressAction,
        key: 'hints.key',
        stage: 'hints.press_stage',
        mods: 'set[hints.press_mod]',
        *args: t.Any,
        **kwargs: t.Any,
    ) -> t.Any:
        if action['type'] != 'press':
            return

        action_keys = set((keys_,)) if isinstance(keys_ := action['key'], str) else set(keys_)
        action_mods = None if (mods_ := action.get('mods')) is None else set((mods_,)) if isinstance(mods_, str) else set(mods_)
        action_stages = (
            None if (stage_ := action.get('stages')) is None else set((stage_,)) if isinstance(stage_, str) else set(stage_)
        )

        if (
            key in action_keys
            and (action_stages is None or stage in action_stages)
            and (action_mods is None or mods == action_mods)
        ):
            self.event.Invoke(key, stage, mods)
