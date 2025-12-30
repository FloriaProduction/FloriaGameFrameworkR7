import typing as t
from uuid import UUID, uuid4
import numpy as np
import itertools

from ... import Abc, Validator, Utils, Convert, GL
from ..Objects.FBO import FBO
from ..Objects.BO import BO
from ..Objects.VAO import VAO
from ...Sequences.InstanceObjectSequence import InstanceObjectSequence
from ...Flag import Flag
from ...Stopwatch import Stopwatch


class BatchGroup:
    __slots__ = (
        'id',
        'batch',
        'ids',
        'update_all',
        'update_pool',
        '_freeze',
        'mesh',
        'material',
        'scheme',
        'instance_dtype',
        'vao',
        'vbo_vertices',
        'vbo_texcoords',
        'vbo_instances',
        'ebo_indices',
        '_update_all_buffer',
        #
        '_stopwatch_SetupGroup',
        '_stopwatch_Update',
        '_stopwatch_Update_All',
        '_stopwatch_Update_Partical',
        '_stopwatch_Draw',
    )

    def __init__(
        self,
        id: int,
        batch: 'Batch',
        obj: Abc.InstanceObject,
    ):
        self.id: int = id

        self.batch = batch

        self.ids: dict[UUID, t.Optional[int]] = {}

        self.update_all: bool = True
        self.update_pool: set[UUID] = set()
        self._freeze = Flag()

        self.mesh = obj.mesh
        self.material: Abc.Material = obj.material
        self.scheme = obj.material.program.scheme
        self.instance_dtype = obj.GetInstanceDType()
        # self.instance_dtype: np.dtype[np.void] = np.dtype(
        #     [
        #         (
        #             item['attrib'],
        #             *Convert.GLSLTypeToNumpy(item['type']),
        #         )
        #         for _, item in self.scheme.get('instance', {}).items()
        #     ]
        # )

        self._update_all_buffer: t.Optional[np.ndarray] = None

        self._stopwatch_SetupGroup = Stopwatch()
        self._stopwatch_Update = Stopwatch()
        self._stopwatch_Update_All = Stopwatch()
        self._stopwatch_Update_Partical = Stopwatch()
        self._stopwatch_Draw = Stopwatch()

        self.vao, self.vbo_vertices, self.vbo_texcoords, self.vbo_instances, self.ebo_indices = self.SetupGroup()

    def SetupGroup(self) -> tuple[VAO, BO, t.Optional[BO], t.Optional[BO], t.Optional[BO]]:
        with self._stopwatch_SetupGroup:
            with self.batch.window.Bind() as window:
                vao = VAO(window)
                with vao.Bind() as vao:
                    vbo_vertices = BO(window, 'array_buffer')
                    with vbo_vertices.Bind() as vbo:
                        if (
                            vertice := next(
                                (item for item in self.scheme['base'].items() if item[1]['attrib'] == 'vertice'),
                                None,
                            )
                        ) is None:
                            raise RuntimeError()

                        vao.VertexAttribPointer(vertice[0], vertice[1]['type'])
                        vbo.SetData(self.mesh.vertices)

                    vbo_texcoords = None
                    if self.mesh.texcoords is not None:
                        vbo_texcoords = BO(window, 'array_buffer')
                        with vbo_texcoords.Bind() as vbo:
                            if (
                                texcoord := next(
                                    (item for item in self.scheme['base'].items() if item[1]['attrib'] == 'texcoord'),
                                    None,
                                )
                            ) is None:
                                raise RuntimeError()

                            vao.VertexAttribPointer(texcoord[0], texcoord[1]['type'])
                            vbo.SetData(self.mesh.texcoords)

                    vbo_instances = None
                    if 'instance' in self.scheme:
                        vbo_instances = BO(window, 'array_buffer')
                        with vbo_instances.Bind():
                            for index, item in self.scheme['instance'].items():
                                vao.VertexAttribPointer(
                                    index,
                                    item['type'],
                                    self.instance_dtype.itemsize,
                                    self.instance_dtype.fields[item['attrib']][1],  # type: ignore
                                    attrib_divisor=1,
                                )

                    ebo_indices = None
                    if self.mesh.indices is not None:
                        ebo_indices = BO(window, 'element_array_buffer')
                        with ebo_indices.Bind() as ebo:
                            ebo.SetData(self.mesh.indices)

            return vao, vbo_vertices, vbo_texcoords, vbo_instances, ebo_indices

    def Register(self, obj: Abc.InstanceObject):
        if self._freeze:
            raise
        if obj.id in self.ids:
            raise RuntimeError()
        self.ids[obj.id] = -1
        self.update_all = True

    def Remove(self, obj: Abc.InstanceObject):
        if self._freeze:
            raise
        if obj.id not in self.ids:
            raise RuntimeError()
        self.ids.pop(obj.id)
        self.update_all = True

    def UpdateObject(self, obj: Abc.InstanceObject):
        if self._freeze:
            raise
        if self.update_all:
            return
        self.update_pool.add(obj.id)

        if (count := self.count) > 0 and len(self.update_pool) / count > 0.5:
            self.update_all = True

    def Update(self):
        with self._stopwatch_Update:
            if self.vbo_instances is None:
                self.update_pool.clear()
                self.update_all = False
                return

            with self._freeze.Bind():
                if self.update_all:
                    with self._stopwatch_Update_All:
                        if self._update_all_buffer is None or self._update_all_buffer.shape[0] != self.count:
                            self._update_all_buffer = np.zeros(self.count, dtype=self.instance_dtype)

                        for offset, id in enumerate(self.ids):
                            self._update_all_buffer[offset] = tuple(self.batch.GetObject(id).GetInstanceData())
                            self.ids[id] = offset

                        with self.vbo_instances.Bind() as vbo:
                            vbo.SetData(self._update_all_buffer, 'stream_draw')

                        self.update_all = False
                        self.update_pool.clear()

                if len(self.update_pool) > 0:
                    with self._stopwatch_Update_Partical:
                        sorted_ids = sorted(
                            ((offset, id) for id in self.update_pool if (offset := self.ids[id]) is not None),
                            key=lambda item: item[0],
                        )

                        if len(sorted_ids) == 0:
                            return

                        self.update_pool = self.update_pool.difference(sorted_ids)

                        current_group: list[tuple[t.Any, ...]] = []
                        current_start_offset = sorted_ids[0][0]
                        last_offset = current_start_offset - 1

                        def Flush():
                            nonlocal current_group, current_start_offset
                            if not current_group or self.vbo_instances is None:
                                return

                            with self.vbo_instances.Bind() as vbo:
                                vbo.SetSubData(
                                    current_start_offset * self.instance_dtype.itemsize,
                                    np.array(current_group, dtype=self.instance_dtype),
                                )
                            current_group.clear()

                        for offset, id in sorted_ids:
                            if offset > last_offset + 1 and current_group:
                                Flush()
                                current_start_offset = offset

                            current_group.append(tuple(self.batch.GetObject(id).GetInstanceData()))
                            last_offset = offset

                        Flush()

    def Draw(self, camera: Abc.Camera):
        with self._stopwatch_Draw:
            with self.vao.Bind():
                with self.material.Bind(camera):
                    if self.mesh.indices is None or self.ebo_indices is None:
                        GL.Draw.ArraysInstanced(
                            self.mesh.primitive,
                            self.mesh.count,
                            self.count,
                        )
                    else:
                        with self.ebo_indices.Bind():
                            GL.Draw.ElementsInstanced(
                                self.mesh.primitive,
                                len(self.mesh.indices),
                                self.count,
                            )

    @property
    def count(self) -> int:
        return len(self.ids)

    def __len__(self):
        return self.count

    @property
    def empty(self):
        return self.count == 0


class Batch(
    Abc.Batch,
):
    __slots__ = (
        '_id',
        '_name',
        '_window',
        '_index',
        '_program_compose',
        '_depth_func',
        '_blend_equation',
        '_blend_factors',
        '_fbo',
        '_vao_quad',
        '_storage',
        '_groups',
        '_stopwatch_Render',
        '_stopwatch_Draw',
    )

    def __init__(
        self,
        window: Abc.Window,
        index: int = 0,
        name: t.Optional[str] = None,
        *,
        program_compose: t.Optional[Abc.ComposeShaderProgram] = None,
        vao_quad: t.Optional[VAO] = None,
    ):
        self._id: UUID = uuid4()
        self._name: t.Optional[str] = name

        self._window = Validator.Instance(window, Abc.Window)
        self._index: int = index

        self._program_compose: Abc.ComposeShaderProgram
        if program_compose is None:
            from ..ShaderPrograms.ComposeShaderProgram import ComposeShaderProgram

            self._program_compose = ComposeShaderProgram(window)
        else:
            self._program_compose = program_compose

        self._storage: dict[UUID, Abc.InstanceObject] = {}
        self._groups: dict[int, BatchGroup] = {}

        self._vao_quad: VAO
        if vao_quad is None:
            with self.window.Bind():
                self._vao_quad = VAO.NewQuad(window)
        else:
            self._vao_quad = vao_quad

        self._fbo: t.Optional[FBO] = None

        self._stopwatch_Render = Stopwatch()
        self._stopwatch_Draw = Stopwatch()

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        self.RemoveAll()

    def Render(self, camera: Abc.Camera):
        with self._stopwatch_Render:
            if self._fbo is None or self._fbo.size != self.window.camera.resolution:
                self._fbo = FBO(self.window, self.window.camera.resolution)

            with self.fbo.Bind():
                GL.ClearColor((0, 0, 0, 0))
                GL.Clear('color', 'depth')

                for group in (*self._groups.values(),):
                    if group.update_all or len(group.update_pool) > 0:
                        group.Update()

                    group.Draw(camera)

    def Draw(self):
        with self._stopwatch_Draw:
            with self._vao_quad.Bind():
                with self.program_compose.Bind(self.fbo):
                    GL.Draw.Arrays('triangle_fan', 4)

    def _RegisterGroup[TGroup: BatchGroup](self, group: TGroup) -> TGroup:
        if group.id in self._groups:
            raise RuntimeError()
        self._groups[group.id] = group
        return group

    def _RemoveGroupByID(self, id: int) -> BatchGroup:
        return self._groups.pop(id)

    def _RemoveGroup[TGroup: BatchGroup](self, group: TGroup) -> TGroup:
        self._RemoveGroupByID(group.id)
        return group

    def _ClearGroupsFromObject[TObj: Abc.InstanceObject](self, obj: TObj) -> TObj:
        for group in filter(
            lambda group: obj.id in group.ids,
            tuple(self._groups.values()),
        ):
            group.Remove(obj)
            if group.empty:
                self._RemoveGroupByID(group.id)
        return obj

    def UpdateObject[TObj: Abc.InstanceObject](self, obj: TObj) -> TObj:
        if not self.Has(obj):
            raise

        group_id = obj.GetSignature()
        group = self._groups.get(group_id)

        if group is None or obj.id not in group.ids:
            self._ClearGroupsFromObject(obj)

            group = self._RegisterGroup(BatchGroup(group_id, self, obj)) if group is None else group
            group.Register(obj)

        group.UpdateObject(obj)

        return obj

    def UpdateMaterial(self, material: Abc.Material[Abc.Graphic.ShaderPrograms.BatchShaderProgram]):
        for group in filter(lambda group: group.material.id == material.id, self._groups.values()):
            group.update_all = True

    def Register[TObj: Abc.InstanceObject](self, item: TObj) -> TObj:
        if item.id in self._storage:
            raise RuntimeError()

        self._storage[item.id] = item
        self.UpdateObject(item)

        return item

    @t.overload
    def Remove[TItem: Abc.InstanceObject](self, item: TItem, /) -> TItem: ...
    @t.overload
    def Remove[TItem: Abc.InstanceObject, TDefault: t.Any](self, item: TItem, default: TDefault, /) -> TItem | TDefault: ...
    def Remove(self, *args: Abc.InstanceObject | t.Any):
        obj = t.cast(Abc.InstanceObject, args[0])

        if obj.id not in self._storage:
            if len(args) == 1:
                raise RuntimeError()
            return args[1]

        self._storage.pop(obj.id)
        self._ClearGroupsFromObject(obj)

        return obj

    def RemoveAll(self):
        for item in (*self.sequence,):
            if (item := self.Remove(item, None)) is not None and isinstance(item, Abc.Mixins.Disposable):
                item.Dispose()

    def Has(self, item: Abc.InstanceObject) -> bool:
        return item.id in self._storage

    def HasID(self, id: UUID) -> bool:
        return id in self._storage

    def GetObject(self, id: UUID, /) -> Abc.InstanceObject:
        return self._storage[id]

    @property
    def sequence(self):
        return InstanceObjectSequence(self._storage.values())

    @property
    def window(self):
        return self._window

    @property
    def fbo(self):
        if self._fbo is None:
            raise RuntimeError()
        return self._fbo

    def GetName(self) -> str | None:
        return self._name

    def GetID(self):
        return self._id

    @property
    def index(self):
        return self._index

    @property
    def program_compose(self):
        return self._program_compose

    @property
    def count(self):
        return len(self._storage)
