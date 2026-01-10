import typing as t

from ... import Abc, Types, Validator, Utils, Protocols
from ...Core import Core
from ...Timer import VariableTimer
from ...Stopwatch import stopwatch
from .InstanceObject import InstanceObject
from ...InterpolationField import InterpolationField


class InterpolationInstanceObject[
    TMaterial: Abc.Material = Abc.Material,
](
    InstanceObject[TMaterial],
):
    ATTRIBS = InstanceObject.ATTRIBS

    __slots__ = (
        '_last_position',
        '_last_scale',
        '_update_transform_event_id',
        '_update_transform_reduce_timer',
        '_update_transform_position_tick',
        '_update_transform_scale_tick',
        #
        '_interp_position',
        '_interp_scale',
        '_interp_rotation',
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
        super().__init__(
            batch,
            material,
            mesh,
            position,
            rotation,
            scale,
            batch_register,
            *args,
            **kwargs,
        )

        self._interp_position = InterpolationField[Types.Vec3[float]](
            Types.Vec3[float].New(position),
            lambda prev, next, progress: Types.Vec3[float].New(Utils.SmoothIter(prev, next, progress)),
            lambda _: self._UpdateInstanceAttributes('model_matrix'),
            self.batch.window.on_simulate,
        )
        self._interp_scale = InterpolationField[Types.Vec3[float]](
            Types.Vec3[float].New(scale),
            lambda prev, next, progress: Types.Vec3[float].New(Utils.SmoothIter(prev, next, progress)),
            lambda _: self._UpdateInstanceAttributes('model_matrix'),
            self.batch.window.on_simulate,
        )
        self._interp_rotation = InterpolationField[Types.Quaternion[float]](
            Types.Quaternion[float].New(rotation),
            lambda prev, next, progress: Types.Quaternion[float].New(Utils.Slerp(prev, next, progress)),
            lambda _: self._UpdateInstanceAttributes('model_matrix'),
            self.batch.window.on_simulate,
        )

    def GetPosition(self) -> Types.Vec3[float]:
        return self._interp_position.GetValue()

    def SetPosition(
        self,
        value: Types.hints.position_3d,
        flash: bool = True,
    ):
        self._interp_position.SetValue(Types.Vec3[float].New(value), flash)

    @property
    def position(self):
        return self.GetPosition()

    @position.setter
    def position(self, value: Types.hints.position_3d):
        self.SetPosition(value, False)

    def GetScale(self) -> Types.Vec3[float]:
        return self._interp_scale.GetValue()

    def SetScale(
        self,
        value: Types.hints.scale_3d,
        flash: bool = True,
    ):
        self._interp_scale.SetValue(Types.Vec3[float].New(value), flash)

    @property
    def scale(self):
        return self.GetScale()

    @scale.setter
    def scale(self, value: Types.hints.scale_3d):
        self.SetScale(value, False)

    def GetRotation(self) -> Types.Quaternion[float]:
        return self._interp_rotation.GetValue()

    def SetRotation(self, value: Types.hints.rotation, flash: bool = True):
        self._interp_rotation.SetValue(Types.Quaternion[float].New(value), flash)

    @property
    def rotation(self) -> 'Types.Quaternion[float]':
        return self.GetRotation()

    @rotation.setter
    def rotation(self, value: 'Types.hints.rotation'):
        self.SetRotation(value, False)
