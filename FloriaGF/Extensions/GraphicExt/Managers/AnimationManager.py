import typing as t
from PIL.Image import Image

from FloriaGF import Assets, Core, Utils
from FloriaGF.Managers import Manager

from ..Graphic.Animation import Animation
from ..Sequences import AnimationSequence


class AnimationManager(
    Manager[Animation],
):
    @property
    def sequence(self) -> AnimationSequence[Animation]:
        return AnimationSequence(self._storage.values())

    @staticmethod
    def _GetKey(item: Animation) -> t.Any:
        return item.name

    def Register[T: Animation](self, item: T) -> T:
        return t.cast(T, super().Register(item))

    @t.overload
    def Remove[T: Animation](self, item: T, /) -> T: ...
    @t.overload
    def Remove[T: Animation, TDefault: t.Any](self, item: T, default: TDefault, /) -> T | TDefault: ...

    def Remove(self, *args: t.Any):
        return super().Remove(*args)

    async def Load(
        self,
        name: str,
        image: Assets.Image | Image | str,
        count: int = 1,
        duration: float = 0,
        loop: bool = False,
    ) -> Animation:
        '''
        Загружает и регистрирует анимацию
        '''
        return self.Register(
            Animation(
                name,
                image if isinstance(image, Assets.Image | Image) else await Core.asset_manager.LoadFile(image, Assets.Image),
                count,
                duration,
                loop,
            )
        )

    class AnimationInfo(t.TypedDict):
        name: str
        image: Assets.Image | Image | str
        count: t.NotRequired[int]
        duration: t.NotRequired[float]
        loop: t.NotRequired[bool]

    async def LoadMany(self, *items: AnimationInfo):
        '''
        Загружает и регистрирует множество анимаций
        '''
        await Utils.WaitCors(self.Load(**info) for info in items)
