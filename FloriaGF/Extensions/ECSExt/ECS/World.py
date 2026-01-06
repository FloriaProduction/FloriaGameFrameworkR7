import typing as t
from abc import ABC
from uuid import UUID, uuid4
import functools

from FloriaGF import Utils, AsyncEvent

from .Components import Component
from .Systems import EntitySystemAny, GlobalSystemAny, BaseSystem, BaseSystemWithDep

from ..Loggers import ecs_logger


class _ComponentMap:
    def __init__(self, data: dict[t.Type[Component], Component]):
        self._data = data

    def __getitem__[TCom: Component](self, key: t.Type[TCom]) -> TCom:
        return self._data[key]  # pyright: ignore[reportReturnType]

    def Get[
        TCom: Component,
        TDefault: t.Optional[t.Any],
    ](
        self,
        key: t.Type[TCom],
        default: TDefault = None,
    ) -> TCom | TDefault:
        return self._data.get(key, default)  # pyright: ignore[reportReturnType]


class EntityInfo(ABC):
    '''
    Обертка для доступа к свойствам сущности
    '''

    __slots__ = (
        '_world',
        '_entity_id',
    )

    def __init__(
        self,
        world: 'World',
        entity_id: UUID,
    ):
        self._world: 'World' = world
        self._entity_id: UUID = entity_id

    @property
    def world(self):
        return self._world

    @property
    def id(self):
        return self._entity_id

    @property
    def components(self) -> _ComponentMap:
        return self._world.GetComponents(self.id)

    @property
    def systems(self) -> set[t.Type[EntitySystemAny]]:
        return self._world.GetSystems(self.id)

    @property
    def name(self) -> t.Optional[str]:
        return self._world.GetEntityName(self.id)

    @property
    def tags(self) -> set[str]:
        return self._world.GetTags(self.id)


class World:
    __slots__ = (
        '_entities',
        '_components',
        '_systems',
        '_systems_order',
        '_names',
        '_tags',
        '_global_systems',
        '_global_systems_order',
        #
        'on_component_added',
        'on_component_removed',
        'on_entity_systems_added',
        'on_entity_systems_removed',
        'on_global_system_added',
        'on_global_system_removed',
        'on_entity_name_setted',
        'on_entity_name_removed',
        'on_entity_tags_added',
        'on_entity_tags_removed',
        # ,
        '__weakref__',
    )

    def __init__(self):
        super().__init__()

        self._entities: set[UUID] = set()

        self._components: dict[t.Type[Component], dict[UUID, Component]] = {}
        self._systems: dict[t.Type[EntitySystemAny], set[UUID]] = {}
        self._systems_order: t.Optional[tuple[t.Type[EntitySystemAny], ...]] = None

        # TODO: добавить обратную индексацию для имен и тегов

        self._names: dict[str, set[UUID]] = {}
        self._tags: dict[str, set[UUID]] = {}

        self._global_systems: set[t.Type[GlobalSystemAny]] = set()
        self._global_systems_order: t.Optional[tuple[t.Type[GlobalSystemAny], ...]] = None

        # events

        self.on_component_added = AsyncEvent[t.Self, UUID, dict[t.Type[Component], Component]]()
        self.on_component_removed = AsyncEvent[t.Self, UUID, dict[t.Type[Component], Component]]()

        self.on_entity_systems_added = AsyncEvent[t.Self, UUID, set[t.Type[EntitySystemAny]]]()
        self.on_entity_systems_removed = AsyncEvent[t.Self, UUID, set[t.Type[EntitySystemAny]]]()

        self.on_global_system_added = AsyncEvent[t.Self, set[t.Type[GlobalSystemAny]]]()
        self.on_global_system_removed = AsyncEvent[t.Self, set[t.Type[GlobalSystemAny]]]()

        self.on_entity_name_setted = AsyncEvent[t.Self, UUID, t.Optional[str], str]()
        self.on_entity_name_removed = AsyncEvent[t.Self, UUID, str]()

        self.on_entity_tags_added = AsyncEvent[t.Self, UUID, set[str]]()
        self.on_entity_tags_removed = AsyncEvent[t.Self, UUID, set[str]]()

    def CreateEntity(
        self,
        components: t.Sequence[Component],
        systems: t.Optional[t.Sequence[t.Type[EntitySystemAny]]] = None,
        name: t.Optional[str] = None,
        tags: t.Optional[t.Sequence[str]] = None,
    ) -> UUID:
        id = uuid4()
        self._entities.add(id)

        if name is not None:
            self.SetEntityName(id, name)

        if tags is not None and len(tags) > 0:
            self.AddTags(id, tags)

        self.AddComponents(id, components)

        systems_ = set[t.Type[EntitySystemAny]]()
        if systems is not None:
            systems_.update(systems)

        for com in components:
            systems_.update(com.GetSystems())

        if len(systems_) > 0:
            self.AddSystems(id, systems_)

        return id

    @t.overload
    def GetEntity(
        self,
        entity_id: UUID,
        /,
    ) -> EntityInfo: ...

    @t.overload
    def GetEntity(
        self,
        entity_id: t.Optional[UUID],
        /,
    ) -> t.Optional[EntityInfo]: ...

    def GetEntity(
        self,
        entity_id: t.Optional[UUID],
    ):
        if entity_id is None:
            return None
        if not self.HasEntity(entity_id):
            raise
        return EntityInfo(self, entity_id)

    def GetEntities(
        self,
    ) -> set[UUID]:
        return set(self._entities)

    def GetEntitiesByComponents[
        TCom: Component = Component,
    ](
        self,
        components: t.Iterable[t.Type[TCom]],
    ) -> set[UUID]:
        return functools.reduce(
            set[UUID].intersection,
            (set(values.keys()) for com_type in components if (values := self._components.get(com_type)) is not None),
        )

    def GetEntitiesByComponent(
        self,
        component: t.Type[Component],
    ) -> set[UUID]:
        return set(self._components[component].keys())

    def GetEntitiesByTags(self, tags: t.Iterable[str]):
        return set(
            functools.reduce(
                set[UUID].intersection,
                (ids for tag in tags if (ids := self._tags.get(tag)) is not None),
            )
        )

    def GetEntitiesByTag(
        self,
        tag: str,
    ) -> set[UUID]:
        return set(self._tags.get(tag, ()))

    def GetEntitiesByNames[
        TName: str,
    ](
        self,
        names: t.Sequence[TName],
    ) -> dict[TName, set[UUID]]:
        result: dict[str, set[UUID]] = {}

        for name, ids in self._names.items():
            if name not in names:
                continue
            result[name] = ids

        return result  # pyright: ignore[reportReturnType]

    def GetEntitiesByName(
        self,
        name: str,
    ) -> set[UUID]:
        return set(self._names.get(name, ()))

    def HasEntity(
        self,
        entity_id: UUID,
    ) -> bool:
        return entity_id in self._entities

    def RemoveEntity(
        self,
        entity_id: UUID,
    ) -> t.Optional[UUID]:
        if not self.HasEntity(entity_id):
            return None

        self.RemoveSystems(entity_id)
        self.RemoveComponents(entity_id)
        self.RemoveTags(entity_id)
        self.RemoveEntityName(entity_id)

        self._entities.remove(entity_id)

        return entity_id

    def SetEntityName(
        self,
        entity_id: UUID,
        name: str,
    ) -> UUID:
        if not self.HasEntity(entity_id):
            raise

        old_name: t.Optional[str] = None

        if name in self._names:
            if entity_id in self._names[name]:
                old_name = name
            self._names[name].add(entity_id)

        else:
            self._names[name] = set((entity_id,))

        self.on_entity_name_setted.Invoke(self, entity_id, old_name, name)

        return entity_id

    def GetEntityName(
        self,
        entity_id: UUID,
    ) -> t.Optional[str]:
        if not self.HasEntity(entity_id):
            raise

        for name, ids in self._names.items():
            if entity_id in ids:
                return name

        return None

    def RemoveEntityName(
        self,
        entity_id: UUID,
    ) -> t.Optional[str]:
        if not self.HasEntity(entity_id):
            raise

        old_name: t.Optional[str] = None

        for name, ids in self._names.items():
            if entity_id in ids:
                old_name = name

                self._names[name].remove(entity_id)

                if len(self._names[name]) == 0:
                    self._names.pop(name)

                break

        if old_name is not None:
            self.on_entity_name_removed.Invoke(self, entity_id, old_name)

        return old_name

    def AddTags(
        self,
        entity_id: UUID,
        tags: t.Iterable[str],
    ) -> UUID:
        if not self.HasEntity(entity_id):
            raise

        result: list[str] = []

        for tag in tags:
            if tag not in self._tags:
                self._tags[tag] = set()

            self._tags[tag].add(entity_id)
            result.append(tag)

        self.on_entity_tags_added.Invoke(self, entity_id, set(result))

        return entity_id

    def GetTags(
        self,
        entity_id: UUID,
    ) -> set[str]:
        if not self.HasEntity(entity_id):
            raise

        result: list[str] = []

        for tag, ids in self._tags.items():
            if entity_id in ids:
                result.append(tag)

        return set(result)

    def RemoveTags(
        self,
        entity_id: UUID,
        tags: t.Optional[t.Iterable[str]] = None,
    ) -> set[str]:
        if not self.HasEntity(entity_id):
            raise

        result: list[str] = []

        for tag in tuple(self._tags.keys()) if tags is None else (tag for tag in tags if tag in self._tags):
            if entity_id in self._tags[tag]:
                self._tags[tag].remove(entity_id)
                result.append(tag)
                if len(self._tags[tag]) == 0:
                    self._tags.pop(tag)

        result_set = set(result)

        self.on_entity_tags_removed.Invoke(self, entity_id, result_set)

        return result_set

    def AddComponents(
        self,
        entity_id: UUID,
        components: t.Iterable[Component],
    ) -> UUID:
        if not self.HasEntity(entity_id):
            raise

        result: dict[t.Type[Component], Component] = {}

        for com in components:
            if (com_type := type(com)) not in self._components:
                self._components[com_type] = {}
            self._components[com_type][entity_id] = com
            result[com_type] = com

        self.on_component_added.Invoke(self, entity_id, result)

        return entity_id

    @t.overload
    def GetComponents(
        self,
        entity_id: UUID,
        /,
    ) -> _ComponentMap: ...

    @t.overload
    def GetComponents(
        self,
        entity_id: UUID,
        components: t.Iterable[t.Type[Component]],
        /,
    ) -> t.Optional[_ComponentMap]: ...

    def GetComponents(
        self,
        entity_id: UUID,
        components: t.Optional[t.Iterable[t.Type[Component]]] = None,
    ):
        if not self.HasEntity(entity_id):
            raise

        result: dict[t.Type[Component], Component] = {}

        if components is None:
            result = {
                com_type: com
                for com_type in self._components.keys()
                if (values := self._components.get(com_type)) is not None and (com := values.get(entity_id)) is not None
            }

        else:
            for com_type in (com_type for com_type in components if com_type in self._components):
                if (com := self._components[com_type].get(entity_id)) is None:
                    return None
                result[com_type] = com

        return _ComponentMap(result)

    def RemoveComponents[
        TCom: Component,
    ](
        self,
        entity_id: UUID,
        components: t.Optional[t.Iterable[t.Type[TCom]]] = None,
    ) -> dict[t.Type[TCom], TCom]:
        if not self.HasEntity(entity_id):
            raise

        result: dict[t.Type[TCom], TCom] = {}

        for com_type in (
            tuple(self._components.keys())
            if components is None
            else (com_type for com_type in components if com_type in self._components)
        ):
            if entity_id in self._components[com_type]:
                com = self._components[com_type].pop(entity_id)
                result[com_type] = com  # pyright: ignore[reportArgumentType]

                if len(self._components[com_type]) == 0:
                    self._components.pop(com_type)

        self.on_component_removed.Invoke(self, entity_id, result)  # pyright: ignore[reportArgumentType]

        return result

    def AddSystems(
        self,
        entity_id: UUID,
        systems: t.Iterable[t.Type[EntitySystemAny]],
    ) -> UUID:
        if not self.HasEntity(entity_id):
            raise

        result: list[t.Type[EntitySystemAny]] = []

        for sys in systems:
            if sys not in self._systems:
                self._systems[sys] = set()
            if entity_id not in self._systems[sys]:
                self._systems[sys].add(entity_id)
                result.append(sys)

                sys.OnAdded(self, entity_id)

        self.on_entity_systems_added.Invoke(self, entity_id, set(result))
        self._systems_order = None

        return entity_id

    def GetSystems[
        TSys: EntitySystemAny = EntitySystemAny,
    ](
        self,
        entity_id: UUID,
        systems: t.Optional[t.Iterable[t.Type[TSys]]] = None,
    ) -> set[t.Type[TSys]]:
        if not self.HasEntity(entity_id):
            raise

        result: list[t.Type[TSys]] = []

        for sys in self._systems.keys() if systems is None else (sys for sys in systems if sys in self._systems):
            if entity_id in self._systems[sys]:
                result.append(sys)  # pyright: ignore[reportArgumentType]

        return set(result)

    def HasSystem(
        self,
        entity_id: UUID,
        system: t.Type[EntitySystemAny],
    ) -> bool:
        return entity_id in self._systems.get(system, ())

    def RemoveSystems[
        TSys: EntitySystemAny = EntitySystemAny,
    ](
        self,
        entity_id: UUID,
        systems: t.Optional[t.Iterable[t.Type[TSys]]] = None,
    ) -> set[t.Type[TSys]]:
        if not self.HasEntity(entity_id):
            raise

        result: list[t.Type[TSys]] = []

        for sys in tuple(self._systems.keys()) if systems is None else (sys for sys in systems if sys in self._systems):
            if entity_id in self._systems[sys]:
                self._systems[sys].remove(entity_id)
                result.append(sys)  # pyright: ignore[reportArgumentType]

                sys.OnRemoved(self, entity_id)

        result_set = set(result)

        self.on_entity_systems_removed.Invoke(self, entity_id, result_set)

        return result_set

    def AddGlobalSystems(
        self,
        systems: t.Iterable[t.Type[GlobalSystemAny]],
    ):
        result: list[t.Type[GlobalSystemAny]] = []

        for sys in (sys for sys in systems if sys not in self._global_systems):
            self._global_systems.add(sys)
            result.append(sys)

            sys.OnAdded(self)

        self.on_global_system_added.Invoke(self, set(result))
        self._global_systems_order = None

    def GetGlobalSystems[
        TSys: GlobalSystemAny = GlobalSystemAny,
    ](
        self,
        systems: t.Optional[t.Iterable[t.Type[TSys]]] = None,
    ) -> set[t.Type[TSys]]:
        return set(self._global_systems if systems is None else (sys for sys in systems if sys in self._global_systems))

    def HasGlobalSystem(
        self,
        system: t.Type[GlobalSystemAny],
    ) -> bool:
        return system in self._global_systems

    def RemoveGlobalSystems[
        TSys: GlobalSystemAny = GlobalSystemAny,
    ](
        self,
        systems: t.Optional[t.Iterable[t.Type[TSys]]] = None,
    ) -> set[t.Type[TSys]]:
        result: list[t.Type[TSys]] = []

        for sys in self.GetGlobalSystems(systems):
            self._global_systems.remove(sys)
            result.append(sys)

            sys.OnRemoved(self)

        result_set = set(result)

        self.on_global_system_removed.Invoke(self, result_set)

        return result_set

    @staticmethod
    def _SortSystems[
        TSys: BaseSystem,
    ](
        systems: t.Sequence[t.Type[TSys]],
    ) -> tuple[t.Type[TSys], ...]:

        graph: dict[t.Type[BaseSystem], list[t.Type[BaseSystem]]] = {}
        in_degree: dict[t.Type[BaseSystem], int] = {}

        for sys in systems:
            if not issubclass(sys, BaseSystemWithDep):
                continue

            for dep in sys.__dependencies__:  # type: ignore
                if dep in systems:
                    if dep not in graph:
                        graph[dep] = []
                    graph[dep].append(sys)  # pyright: ignore[reportUnknownArgumentType]

                    if sys not in in_degree:
                        in_degree[sys] = 0
                    in_degree[sys] += 1

        queue: list[t.Type[BaseSystem]] = [sys for sys in systems if in_degree.get(sys, 0) == 0]
        result: list[t.Type[BaseSystem]] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            if current not in graph:
                continue

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(systems):
            raise

        return (*result,)  # pyright: ignore[reportReturnType]

    async def Simulate(self, *args: t.Any, **kwargs: t.Any):
        cors: list[t.Coroutine[t.Any, t.Any, t.Any]] = []

        if self._systems_order is None:
            self._systems_order = self._SortSystems((*self._systems.keys(),))

        for sys in self._systems_order:
            with Utils.ExceptionHandler(lambda _: ecs_logger.error('', exc_info=True)):
                if isinstance(result := sys.SimulateBatch(self, set(self._systems[sys])), t.Coroutine):
                    cors.append(result)

        if self._global_systems_order is None:
            self._global_systems_order = self._SortSystems((*self._global_systems,))

        for sys in self._global_systems_order:
            with Utils.ExceptionHandler(lambda _: ecs_logger.error('', exc_info=True)):
                if isinstance(result := sys.Simulate(self), t.Coroutine):
                    cors.append(result)

        with Utils.ExceptionHandler(lambda _: ecs_logger.error('', exc_info=True)):
            await Utils.WaitCors(cors)
