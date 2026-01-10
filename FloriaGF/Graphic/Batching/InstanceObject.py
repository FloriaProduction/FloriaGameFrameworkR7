import typing as t
from uuid import uuid4, UUID
import glm
import numpy as np

from ... import Abc, Types, Validator
from ...Stopwatch import stopwatch


class InstanceObject[
    TMaterial: Abc.Material = Abc.Material,
](
    Abc.Graphic.Batching.InstanceObject,
):
    ATTRIBS = t.Literal['model_matrix'] | str

    __slots__ = (
        '_id',
        #
        '_position',
        '_rotation',
        '_scale',
        #
        '_material',
        '_mesh',
        '_batch',
        #
        '__update_instance_fields',
        '__instance_data_cache',
        '_model_mat',
    )

    def __init__(
        self,
        batch: Abc.Graphic.Batching.Batch,
        material: TMaterial,
        mesh: Abc.Graphic.Mesh,
        position: Types.hints.position_3d,
        rotation: Types.hints.rotation,
        scale: Types.hints.scale_3d,
        batch_register: bool = True,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        super().__init__()

        self._id: UUID = uuid4()

        self._position: Types.Vec3[float] = Types.Vec3[float].New(position)
        self._rotation: Types.Quaternion[float] = Types.Quaternion[float].New(rotation)
        self._scale: Types.Vec3[float] = Types.Vec3[float].New(scale)

        self._model_mat: t.Optional[np.typing.NDArray[np.float32]] = None

        self._material = t.cast(TMaterial, Validator.Instance(material, Abc.Graphic.Materials.Material))
        self._mesh = Validator.Instance(mesh, Abc.Graphic.Mesh)
        self._batch = Validator.Instance(batch, Abc.Graphic.Batching.Batch)

        if batch_register:
            self.batch.Register(self)

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        self.batch.Remove(self, None)

    def GetIntanceAttributeItems(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem[InstanceObject.ATTRIBS], ...]:
        return tuple(self.material.program.scheme.get('instance', {}).values())

    def _GetInstanceAttribute(self, name: InstanceObject.ATTRIBS) -> t.Any:
        if name == 'model_matrix':
            return self._GetModelMatrix(
                self.position,
                self.rotation,
                self.scale,
            )

        raise RuntimeError()

    def _GetInstanceAttributeCache(self, name: InstanceObject.ATTRIBS) -> t.Optional[t.Any]:
        return super()._GetInstanceAttributeCache(name)

    def _UpdateInstanceAttributes(self, *names: InstanceObject.ATTRIBS, all: bool = False):
        update = self.request_intance_update is False  # Если до вызова обновление не требовалось, то обновляем Batch

        super()._UpdateInstanceAttributes(*names, all=all)

        if update:
            self._UpdateBatch()

    def GetID(self):
        return self._id

    def GetPosition(self) -> Types.Vec3[float]:
        return self._position

    def SetPosition(self, value: Types.hints.position_3d):
        self._position = Types.Vec3[float].New(value)
        self._UpdateInstanceAttributes('model_matrix')

    def GetRotation(self) -> Types.Quaternion[float]:
        return self._rotation

    def SetRotation(self, value: Types.hints.rotation):
        self._rotation = Types.Quaternion[float].New(value)
        self._UpdateInstanceAttributes('model_matrix')

    def GetScale(self) -> Types.Vec3[float]:
        return self._scale

    def SetScale(self, value: Types.hints.scale_3d):
        self._scale = Types.Vec3[float].New(value)
        self._UpdateInstanceAttributes('model_matrix')

    @property
    def batch(self):
        return self._batch

    @property
    def mesh(self):
        return self._mesh

    @property
    def material(self):
        return self._material

    @staticmethod
    @stopwatch
    def _GetModelMatrix(
        position: Types.Vec3[float],
        rotation: Types.Quaternion[float],
        scale: Types.Vec3[float],
    ) -> tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ]:
        return (
            glm.translate(glm.mat4(1), glm.vec3(*position)) * glm.mat4_cast(rotation) * glm.scale(glm.mat4(1.0), glm.vec3(*scale))
        ).to_tuple()

    def SetMaterial(self, value: TMaterial, *, update_batch: bool = True) -> TMaterial:
        self._material = value
        if update_batch:
            self._UpdateBatch()
        return self.material

    def _UpdateBatch(self, *args: t.Any, **kwargs: t.Any):
        '''
        Попроситься обновиться в Batch
        '''
        if self in self.batch:
            self.batch.UpdateObject(self)

    def GetSignature(self) -> int:
        return hash(
            (
                self.mesh.GetSignature(),
                self.material.GetSignature(),
            )
        )
