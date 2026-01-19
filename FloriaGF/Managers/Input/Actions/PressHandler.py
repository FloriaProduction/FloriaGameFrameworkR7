import typing as t

from .Action import Action, KeyboardHandler

if t.TYPE_CHECKING:
    from ....AsyncEvent import AsyncEvent
    from .. import hints


class PressAction(Action, t.TypedDict):
    key: 'hints.key | t.Iterable[hints.key]'
    mods: 't.NotRequired[hints.press_mod | t.Iterable[hints.press_mod]]'
    stages: 't.NotRequired[hints.press_stage | t.Sequence[hints.press_stage]]'


class PressHandler(
    KeyboardHandler['AsyncEvent[hints.key,hints.press_stage,set[hints.press_mod]]'],
):
    def Simulate(
        self,
        action: PressAction,
        key: 'hints.key',
        stage: 'hints.press_stage',
        mods: 'set[hints.press_mod]',
        *args: t.Any,
        **kwargs: t.Any,
    ) -> t.Any:
        action_keys = set((keys_,)) if isinstance(keys_ := action['key'], str) else set(keys_)
        action_mods = (
            set((mods_,))
            if isinstance(mods_ := t.cast('hints.press_mod | t.Iterable[hints.press_mod]', action.get('mods', ())), str)
            else set(mods_)
        )
        action_stages = (
            set((stage_,))
            if isinstance(stage_ := t.cast('hints.press_stage | t.Sequence[hints.press_stage]', action.get('stages', ())), str)
            else set(stage_)
        )

        if key in action_keys and stage in action_stages and mods == action_mods:
            self.event.Invoke(key, stage, mods)
