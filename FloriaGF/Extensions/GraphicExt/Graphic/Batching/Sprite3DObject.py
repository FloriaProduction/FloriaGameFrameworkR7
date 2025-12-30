import typing as t
import numpy as np
from pyrr import Vector3
from time import perf_counter

from FloriaGF import Abc, Core, Validator, Utils, Types, Convert, VariableTimer, Stopwatch
from FloriaGF import AsyncEvent
from FloriaGF.Graphic.Batching import InterpolationInstanceObject
from FloriaGF.Types.Vec import Vec3

from ..Materials.Sprite3DMaterial import Sprite3DMaterial
from .. import Meshes

if t.TYPE_CHECKING:
    from ..Animation import Animation


class Sprite3DObject[
    TMaterial: Sprite3DMaterial = Sprite3DMaterial,
](
    InterpolationInstanceObject[TMaterial],
):
    ATTRIBS = t.Union[
        InterpolationInstanceObject.ATTRIBS,
        t.Literal[
            'opacity',
            'frame',
        ],
    ]

    MATERIAL_NAME = 'sprite-3d-material'
    MESH_NAME = 'sprite-3d-mesh'

    REDUCED_INTERVAL_UPDATE_ANIMATION = 1 / 30

    @classmethod
    def New(
        cls,
        batch: Abc.Batch,
        animation: t.Optional['Animation'] = None,
        position: Types.hints.position_3d = (0, 0, 0),
        rotation: Types.hints.rotation = (0, 0, 0),
        scale: t.Optional[Types.hints.scale_3d] = None,
        opacity: float = 1,
        visible: bool = True,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        material = batch.window.material_manager.sequence.OfType(Sprite3DMaterial).GetByNameOrDefaultLazy(
            cls.MATERIAL_NAME,
            lambda: batch.window.material_manager.Register(Sprite3DMaterial.New(batch.window, animation, cls.MATERIAL_NAME)),
        )

        mesh = Core.mesh_manager.sequence.GetByNameOrDefaultLazy(
            cls.MESH_NAME,
            lambda: Core.mesh_manager.Register(Meshes.CreateSpriteMesh(cls.MESH_NAME)),
        )

        return Sprite3DObject(
            batch,
            material,
            mesh,
            animation,
            position,
            rotation,
            scale,
            opacity,
            visible,
        )

    def __init__(
        self,
        batch: Abc.Batch,
        material: TMaterial,
        mesh: Abc.Mesh,
        animation: t.Optional['Animation'],
        position: Types.hints.position_3d,
        rotation: Types.hints.rotation,
        scale: t.Optional[Types.hints.scale_3d] = None,
        opacity: float = 1,
        visible: bool = True,
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
            1 if scale is None else scale,
            batch_register,
            *args,
            **kwargs,
        )

        self._update_animation_event_id: t.Optional[int] = None
        self._update_animation_reduce_timer = VariableTimer(self.REDUCED_INTERVAL_UPDATE_ANIMATION)
        self._update_animation_opacity_tick: t.Optional[int] = None

        self._last_opacity: t.Optional[float] = None
        self._opacity: float = opacity

        self._visible: bool = visible

        self._start_time: float = 0
        self._pause_time: t.Optional[float] = None

        self._on_change_frame = AsyncEvent[t.Self, 'Animation', int]()
        self._on_end_animation = AsyncEvent[t.Self, 'Animation']()
        self._on_change_animation = AsyncEvent[t.Self, t.Optional['Animation']]()
        self._on_pause = AsyncEvent[t.Self, 'Animation', bool]()

        self._stopwatch_UpdateAnimation = Stopwatch()

        self.SetAnimation(animation, scale=scale is None)

    def UpdateAnimation(self, *args: t.Any, **kwargs: t.Any):
        with self._stopwatch_UpdateAnimation:
            if not self._update_animation_reduce_timer.Try():
                return

            update_animation = (anim := self.animation) is not None and anim.count > 1
            update_opacity = self._last_opacity is not None

            if True in (update_animation, update_opacity):
                if update_animation:
                    current_frame = self.frame
                    previous_frame = t.cast(t.Optional[int], self._GetInstanceAttributeCache('frame'))

                    if current_frame == previous_frame:
                        return

                    # TODO: доработать события смены кадра и завершения цикла

                    self._UpdateInstanceAttributes('frame')

                if update_opacity:
                    self._UpdateInstanceAttributes('opacity')

            else:
                self._RemoveEventUpdateAnimation()
                return

    def _RemoveEventUpdateAnimation(self):
        if self._update_animation_event_id is not None:
            self._RemoveUpdateEventFunc(self._update_animation_event_id)
            self._update_animation_event_id = None

    def _RegisterEventUpdateAnimation(self):
        if self._update_animation_event_id is None:
            self._update_animation_event_id = self._RegisterUpdateEventFunc(self.UpdateAnimation)

    def SetAnimation(
        self,
        animation: t.Optional['Animation'],
        *,
        scale: bool = True,
        frame: int = 0,
        pause: bool = False,
    ):
        self.SetMaterial(
            self.material.Modify(animation=animation),
            update_batch=False,
        )
        now = perf_counter()

        if animation is not None:
            self._start_time = now - animation.frame_duration * frame
            self._pause_time = now if pause else None

            if scale:
                super(InterpolationInstanceObject, self).SetScale(Convert.FromPIX(animation.size).ToVec3(0))

            if animation.count > 1 and not pause:
                self._RegisterEventUpdateAnimation()
        else:
            self._start_time = now
            self._pause_time = None

        self._UpdateInstanceAttributes('frame')
        self.on_change_animation.Invoke(self, animation)

    def Play(self):
        if (anim := self.animation) is None or self._pause_time is None:
            return

        time = self._pause_time - self._start_time
        self._start_time = perf_counter() - time
        self._pause_time = None

        self._RegisterEventUpdateAnimation()
        self._UpdateInstanceAttributes('frame')
        self.on_pause.Invoke(self, anim, False)

    def Pause(self):
        if (anim := self.animation) is None or self._pause_time is not None:
            return

        self._pause_time = perf_counter()

        self._RemoveEventUpdateAnimation()
        self._UpdateInstanceAttributes('frame')

        self.on_pause.Invoke(self, anim, True)

    # def _GetIntanceAttributeItems(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem[Sprite3DObject.ATTRIBS], ...]:
    #     return (
    #         *super()._GetIntanceAttributeItems(),
    #         {
    #             'attrib': 'opacity',
    #             'type': 'float',
    #         },
    #         {
    #             'attrib': 'frame',
    #             'type': 'float',
    #         },
    #         # 'opacity',
    #         # 'frame',
    #     )

    def _GetInstanceAttribute(self, attrib: Sprite3DObject.ATTRIBS) -> t.Any:
        if attrib == 'opacity':
            return self.opacity

        elif attrib == 'frame':
            return self.frame

        return super()._GetInstanceAttribute(attrib)

    def _GetInstanceAttributeCache(self, attrib: Sprite3DObject.ATTRIBS) -> t.Optional[t.Any]:
        return super()._GetInstanceAttributeCache(attrib)

    def _UpdateInstanceAttributes(self, *fields: Sprite3DObject.ATTRIBS, all: bool = False):
        return super()._UpdateInstanceAttributes(*fields, all=all)

    @property
    def animation(self) -> t.Optional['Animation']:
        return self.material.animation

    @property
    def paused(self) -> bool:
        return self._pause_time is not None

    def GetOpacity(self) -> float:
        if (
            self._last_opacity is None
            or (progress := Core.sps_timer.GetProgressByTick(Validator.NotNone(self._update_animation_opacity_tick))) >= 1
        ):
            self._last_opacity = None
            return self._opacity

        return Utils.Smooth(
            self._last_opacity,
            self._opacity,
            progress,
        )

    def SetOpacity(
        self,
        value: float,
        flash: bool = True,
    ):
        if flash:
            self._last_opacity = None
        else:
            self._last_opacity = self._opacity
            self._update_animation_opacity_tick = Core.sps_timer.tick
            self._RegisterEventUpdateAnimation()

        self._opacity = max(0, min(1, value))
        self._UpdateInstanceAttributes('opacity')

    @property
    def opacity(self) -> float:
        return self.GetOpacity()

    @opacity.setter
    def opacity(self, value: float):
        self.SetOpacity(value, False)

    @property
    def frame(self) -> int:
        frame: int = 0
        if (anim := self.animation) is not None and anim.count > 1:
            count = round(
                max(
                    ((self._pause_time if self._pause_time is not None else Core.window_manager.simulate_time) - self._start_time)
                    / (anim.duration / anim.count),
                    0,
                )
            )
            frame = count % anim.count if count > 0 and anim.loop else min(count, anim.count - 1)

        return frame

    def GetVisible(self) -> bool:
        return self._visible

    def SetVisible(self, value: bool):
        self._visible = value
        if self.visible:
            if self not in self.batch:
                self.batch.Register(self)
        else:
            self.batch.Remove(self)

    @property
    def visible(self) -> bool:
        return self.GetVisible()

    @visible.setter
    def visible(self, value: bool):
        return self.SetVisible(value)

    @property
    def on_change_frame(self):
        return self._on_change_frame

    @property
    def on_end_animation(self):
        return self._on_end_animation

    @property
    def on_change_animation(self):
        return self._on_change_animation

    @property
    def on_pause(self):
        return self._on_pause
