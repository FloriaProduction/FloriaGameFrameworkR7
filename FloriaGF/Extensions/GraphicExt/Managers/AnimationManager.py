import typing as t
from PIL.Image import Image
from pathlib import Path

from FloriaGF import Assets, Core, Utils, Types
from FloriaGF.Managers import Manager

from ..Graphic.Animation import Animation
from ..Sequences import AnimationSequence


class AnimationManager(
    Manager[Animation],
):
    @staticmethod
    def _GetKey(item: Animation) -> t.Any:
        return item.name

    @property
    def sequence(self) -> AnimationSequence[Animation]:
        return AnimationSequence(self._storage.values())

    async def Load(
        self,
        name: str,
        image: Assets.Image | Image | str,
        count: t.Optional[int] = None,
        start: t.Optional[int] = None,
        duration: t.Optional[float] = None,
        loop: t.Optional[bool] = None,
        orientation: t.Optional[Types.hints.orientation] = None,
        points: t.Optional[t.Mapping[int, t.Mapping['Animation.POINT_NAME', Types.hints.offset_2d]]] = None,
    ) -> Animation:
        '''
        Загружает и регистрирует анимацию
        '''
        return self.Register(
            Animation(
                name,
                image if isinstance(image, Assets.Image | Image) else await Core.asset_manager.LoadFile(image, Assets.Image),
                count,
                start,
                duration,
                loop,
                orientation,
                points,
            )
        )

    class AnimationInfo(t.TypedDict):
        name: str
        image: Assets.Image | Image | str
        count: t.NotRequired[int]
        start: t.NotRequired[int]
        duration: t.NotRequired[float]
        frame_duration: t.NotRequired[float]
        loop: t.NotRequired[bool]
        orientation: t.NotRequired[Types.hints.orientation]
        points: t.NotRequired[t.Mapping[int, t.Mapping['Animation.POINT_NAME', Types.hints.offset_2d]]]

    async def LoadMany(self, *items: AnimationInfo):
        '''
        Загружает и регистрирует множество анимаций
        '''
        await Utils.WaitCors(
            self.Load(
                info['name'],
                info['image'],
                (count := info.get('count')),
                info.get('start'),
                (
                    (
                        (frame_duration * count)
                        if (frame_duration := info.get('frame_duration')) is not None and count is not None
                        else None
                    )
                    if (duration := info.get('duration')) is None
                    else duration
                ),
                info.get('loop'),
                info.get('orientation'),
                info.get('points'),
            )
            for info in items
        )

    class AnimationSheetInfo(t.TypedDict):
        name: str

        offset: Types.hints.offset_2d
        size: Types.hints.size_2d

        count: t.NotRequired[int]
        start: t.NotRequired[int]
        duration: t.NotRequired[float]
        frame_duration: t.NotRequired[float]
        loop: t.NotRequired[bool]
        orientation: t.NotRequired[Types.hints.orientation]
        points: t.NotRequired[t.Mapping[int, t.Mapping['Animation.POINT_NAME', Types.hints.offset_2d]]]

    async def LoadSheet(self, path: str | Path, *items: AnimationSheetInfo):
        if len(items) == 0:
            raise

        sheet_image = await Core.asset_manager.LoadFile(path, Assets.Image)
        if (image := sheet_image.image) is None:
            raise

        for info in items:
            offset = info['offset']
            size = info['size']
            count = info.get('count', 1)
            orientation = info.get('orientation', 'horizontal')

            await self.Load(
                info['name'],
                image.crop(
                    (
                        offset[0],
                        offset[1],
                        offset[0] + size[0] * (count if orientation == 'horizontal' else 1),
                        offset[1] + size[1] * (count if orientation == 'vertical' else 1),
                    )
                ),
                count,
                info.get('start'),
                info.get('frame_duration', 0) * count if (duration := info.get('duration')) is None else duration,
                info.get('loop'),
                orientation,
                info.get('points'),
            )

    if t.TYPE_CHECKING:

        def Register[T: Animation](self, item: T) -> T:
            return t.cast(T, super().Register(item))

        @t.overload
        def Remove[T: Animation](self, item: T, /) -> T: ...
        @t.overload
        def Remove[T: Animation, TDefault: t.Any](self, item: T, default: TDefault, /) -> T | TDefault: ...

        def Remove(self, *args: t.Any):
            return super().Remove(*args)
