import typing as t
import numpy as np
from time import perf_counter

from FloriaGF import Abc, Core, Validator, Utils, Types, Convert, VariableTimer, stopwatch, InterpolationField, InterpolationState
from FloriaGF import AsyncEvent
from FloriaGF.Graphic.Batching import InterpolationInstanceObject

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

        self._interp_animation = InterpolationState(
            lambda: self._UpdateInstanceAttributes('frame'),
            lambda: (anim := self.animation) is not None and anim.count > 1,
            self.batch.window.on_simulate,
        )
        self._interp_opacity = InterpolationField(
            opacity,
            lambda prev, next, progress: Utils.Smooth(prev, next, progress),
            lambda value: self._UpdateInstanceAttributes('opacity'),
            self.batch.window.on_simulate,
        )

        self._opacity: float = opacity
        self._visible: bool = visible

        self._start_time: float = 0
        self._pause_time: t.Optional[float] = None

        self._on_change_frame = AsyncEvent[t.Self, 'Animation', int]()
        self._on_end_animation = AsyncEvent[t.Self, 'Animation']()
        self._on_change_animation = AsyncEvent[t.Self, t.Optional['Animation']]()
        self._on_pause = AsyncEvent[t.Self, 'Animation', bool]()

        self.SetAnimation(animation, scale=scale is None)

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
            # update_batch=False,
        )
        now = perf_counter()

        if animation is not None:
            self._start_time = now - animation.frame_duration * frame
            self._pause_time = now if pause else None

            if scale:
                self.SetScale(Convert.FromPIX(animation.size).ToVec3(0))

            if animation.count > 1 and not pause:
                self._interp_animation.RegisterEvent()
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

        self._interp_animation.RegisterEvent()
        self._UpdateInstanceAttributes('frame')

        self.on_pause.Invoke(self, anim, False)

    def Pause(self):
        if (anim := self.animation) is None or self._pause_time is not None:
            return

        self._pause_time = perf_counter()

        self._interp_animation.RemoveEvent()
        self._UpdateInstanceAttributes('frame')

        self.on_pause.Invoke(self, anim, True)

    def _GetInstanceAttribute(self, name: Sprite3DObject.ATTRIBS) -> t.Any:
        if name == 'opacity':
            return self.opacity

        elif name == 'frame':
            return self.frame

        return super()._GetInstanceAttribute(name)

    def _GetInstanceAttributeCache(self, name: Sprite3DObject.ATTRIBS) -> t.Optional[t.Any]:
        return super()._GetInstanceAttributeCache(name)

    def _UpdateInstanceAttributes(self, *names: Sprite3DObject.ATTRIBS, all: bool = False):
        return super()._UpdateInstanceAttributes(*names, all=all)

    @property
    def animation(self) -> t.Optional['Animation']:
        return self.material.animation

    @property
    def paused(self) -> bool:
        return self._pause_time is not None

    def GetOpacity(self) -> float:
        return self._interp_opacity.GetValue()

    def SetOpacity(
        self,
        value: float,
        flash: bool = True,
    ):
        self._interp_opacity.SetValue(value, flash)

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
