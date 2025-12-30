import typing as t
from abc import ABC, abstractmethod

from FloriaGF import Utils


if t.TYPE_CHECKING:
    from uuid import UUID
    from ..World import World


class BaseSystem(ABC):
    pass


class BaseSystemWithDep[TDep: 'BaseSystem' = 'BaseSystem'](BaseSystem):
    __dependencies__: t.Iterable[t.Type[TDep]] = ()
    '''Зависимости от других систем'''


class BaseEntitySystem(
    BaseSystem,
):
    @classmethod
    def OnAdded(cls, world: 'World', entity_id: 'UUID', *args: t.Any, **kwargs: t.Any):
        '''Событие добавления системы к сущности'''

    @classmethod
    def OnRemoved(cls, world: 'World', entity_id: 'UUID', *args: t.Any, **kwargs: t.Any):
        '''Событие удаления системы из сущности'''


class EntitySystem(
    BaseEntitySystem,
    BaseSystemWithDep['EntitySystem'],
):
    @classmethod
    def SimulateBatch(cls, world: 'World', entity_ids: set['UUID'], *args: t.Any, **kwargs: t.Any):
        for id in entity_ids:
            cls.Simulate(world, id, *args, **kwargs)

    @classmethod
    def Simulate(cls, world: 'World', entity_id: 'UUID', *args: t.Any, **kwargs: t.Any):
        pass


class EntitySystemAsync(
    BaseEntitySystem,
):
    @classmethod
    async def SimulateBatch(cls, world: 'World', entity_ids: set['UUID'], *args: t.Any, **kwargs: t.Any):
        await Utils.WaitCors(
            (
                cls.Simulate(
                    world,
                    id,
                    *args,
                    **kwargs,
                )
                for id in entity_ids
            )
        )

    @classmethod
    async def Simulate(cls, world: 'World', entity_id: 'UUID', *args: t.Any, **kwargs: t.Any):
        pass


EntitySystemAny = t.Union[
    EntitySystem,
    EntitySystemAsync,
]


class BaseGlobalSystem(
    BaseSystem,
):
    @classmethod
    def OnAdded(cls, world: 'World', *args: t.Any, **kwargs: t.Any):
        '''Событие добавления системы к сущности'''

    @classmethod
    def OnRemoved(cls, world: 'World', *args: t.Any, **kwargs: t.Any):
        '''Событие удаления системы из сущности'''


class GlobalSystem(
    BaseGlobalSystem,
    BaseSystemWithDep['GlobalSystem'],
):
    @classmethod
    @abstractmethod
    def Simulate(cls, world: 'World', *args: t.Any, **kwargs: t.Any): ...


class GlobalSystemAsync(BaseGlobalSystem):
    @classmethod
    @abstractmethod
    async def Simulate(cls, world: 'World', *args: t.Any, **kwargs: t.Any): ...


GlobalSystemAny = t.Union[
    GlobalSystem,
    GlobalSystemAsync,
]
