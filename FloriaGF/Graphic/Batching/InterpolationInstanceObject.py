import typing as t

from ... import Abc, Types, Validator, Utils, Convert, Protocols
from ...Core import Core
from ...Timer import VariableTimer
from ...Stopwatch import Stopwatch
from .InstanceObject import InstanceObject


class InterpolationInstanceObject[
    TMaterial: Abc.Material = Abc.Material,
](
    InstanceObject[TMaterial],
):
    ATTRIBS = InstanceObject.ATTRIBS

    UPDATE_TRANSFORM_THRESHOLD_DOWNGRADE = 65
    UPDATE_TRANSFORM_REDUCED_INTERVAL = 1 / 45
    UPDATE_TRANSFORM_MIN_POSITION_DISTANCE = 0.01
    UPDATE_TRANSFORM_MIN_SCALE_DISTANCE = 0.01

    __slots__ = (
        '_last_position',
        '_last_scale',
        '_update_transform_event_id',
        '_update_transform_reduce_timer',
        '_update_transform_position_tick',
        '_update_transform_scale_tick',
        #
        '_stopwatch_UpdateTransform',
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

        self._update_transform_event_id: t.Optional[int] = None
        self._update_transform_reduce_timer = VariableTimer(self.UPDATE_TRANSFORM_REDUCED_INTERVAL)
        self._update_transform_position_tick: t.Optional[int] = None
        self._update_transform_scale_tick: t.Optional[int] = None

        self._last_position: t.Optional[Types.Vec3[float]] = None
        self._last_scale: t.Optional[Types.Vec3[float]] = None

        self._stopwatch_UpdateTransform = Stopwatch()

    def _GetUpdateTick(self):
        return Core.sps_timer.tick

    def _RegisterUpdateEventFunc(self, func: Protocols.Functions.AnyCallable) -> int:
        return self.batch.window.on_simulate.Register(func)

    def _RemoveUpdateEventFunc(self, id: int):
        self.batch.window.on_simulate.Remove(id)

    def UpdateTransform(self, *args: t.Any, **kwargs: t.Any):
        with self._stopwatch_UpdateTransform:
            if (
                self.batch.window.on_simulate.count > self.UPDATE_TRANSFORM_THRESHOLD_DOWNGRADE
                and not self._update_transform_reduce_timer.Try()
            ):
                return

            if Validator.AllIsNone((self._last_position, self._last_scale)):
                self._RemoveEventUpdateTransform()
                return

            self._UpdateInstanceAttributes('model_matrix')

    def _RemoveEventUpdateTransform(self):
        if self._update_transform_event_id is not None:
            self._RemoveUpdateEventFunc(self._update_transform_event_id)
            self._update_transform_event_id = None

    def _RegisterEventUpdateTransform(self):
        if self._update_transform_event_id is None:
            self._update_transform_event_id = self._RegisterUpdateEventFunc(self.UpdateTransform)

    def GetPosition(self) -> Types.Vec3[float]:
        if (
            self._last_position is None
            or (progress := Core.sps_timer.GetProgressByTick(Validator.NotNone(self._update_transform_position_tick))) >= 1
        ):
            self._last_position = None
            return self._next_position

        return Types.Vec3[float].New(
            Utils.SmoothIter(
                self._last_position,
                self._next_position,
                progress,
            )
        )

    def SetPosition(
        self,
        value: Types.hints.position_3d,
        flash: bool = True,
    ):
        if flash:
            self._last_position = None
        else:
            self._last_position = self._next_position
            self._update_transform_position_tick = Core.sps_timer.tick
            self._RegisterEventUpdateTransform()
        return super().SetPosition(value)

    @property
    def position(self):
        return self.GetPosition()

    @position.setter
    def position(self, value: Types.hints.position_3d):
        self.SetPosition(value, False)

    @property
    def _next_position(self):
        return super().GetPosition()

    def GetScale(self) -> Types.Vec3[float]:
        if (
            self._last_scale is None
            or (progress := Core.sps_timer.GetProgressByTick(Validator.NotNone(self._update_transform_scale_tick))) >= 1
        ):
            self._last_scale = None
            return self._next_scale

        return Types.Vec3[float].New(
            Utils.SmoothIter(
                self._last_scale,
                self._next_scale,
                progress,
            )
        )

    def SetScale(
        self,
        value: Types.hints.scale_3d,
        flash: bool = True,
    ):
        if flash:
            self._last_scale = None
        else:
            self._last_scale = self._next_scale
            self._update_transform_scale_tick = Core.sps_timer.tick
            self._RegisterEventUpdateTransform()
        return super().SetScale(value)

    @property
    def scale(self):
        return self.GetScale()

    @scale.setter
    def scale(self, value: Types.hints.scale_3d):
        self.SetScale(value, False)

    @property
    def _next_scale(self):
        return super().GetScale()
