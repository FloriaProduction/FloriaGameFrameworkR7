import typing as t
from abc import ABC, abstractmethod
from uuid import UUID

from .... import Types, Abc
from ....AsyncEvent import AsyncEvent
from .. import hints

if t.TYPE_CHECKING:
    from ..InputManager import InputManager


TEvent = t.TypeVar(
    'TEvent',
    bound=AsyncEvent[...],
    default=AsyncEvent[...],
    covariant=True,
)


class Action(t.TypedDict):
    type: hints.action_type


class ActionHandler(
    ABC,
    t.Generic[TEvent],
):
    @abstractmethod
    def Simulate(self, action: 'Action', *args: t.Any, **kwargs: t.Any) -> t.Any: ...

    def __init__(self, input_manager: 'InputManager', map: str, action: str, *args: t.Any, **kwargs: t.Any):
        self.event = t.cast(TEvent, AsyncEvent[...]())

        self._ids: dict[UUID, set[UUID]] = t.DefaultDict(lambda: set())
        '''
        Example:: 
        
            {
                input_manager.id: set(
                    input_manager.RegisterActionHandler(...),
                    ...
                ),
                ...
            }
        '''

        self.Register(input_manager, map, action)

    def Register(self, input_manager: 'InputManager', map: str, action: str, *args: t.Any, **kwargs: t.Any):
        self._ids[input_manager.id].add(input_manager.RegisterHandler(self, map, action))

    def Remove(self, input_manager: 'InputManager'):
        input_manager.RemoveHandlers(self._ids[input_manager.id])


class KeyboardHandler[TEvent: AsyncEvent[...] = AsyncEvent[...]](ActionHandler[TEvent]):
    @abstractmethod
    def Simulate(
        self,
        action: 'Action',
        key: hints.key,
        stage: hints.press_stage,
        mods: set[hints.press_mod],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> t.Any: ...
