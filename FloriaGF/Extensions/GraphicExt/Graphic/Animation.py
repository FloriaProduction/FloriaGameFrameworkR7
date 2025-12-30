import typing as t
from PIL.Image import Image

from FloriaGF import Abc, Types, Validator

if t.TYPE_CHECKING:
    from FloriaGF import Assets


class Animation(Abc.Mixins.Signaturable):
    __slots__ = (
        '_name',
        '_image',
        '_count',
        '_duration',
        '_loop',
    )

    def __init__(
        self,
        name: str,
        image: 'Assets.Image | Image',
        count: int = 1,
        duration: float = 0,
        loop: bool = False,
    ):
        super().__init__()

        self._name: str = name
        self._image: 'Image' = image if isinstance(image, Image) else Validator.NotNone(image.image)
        self._count: int = count
        self._duration: float = duration
        self._loop: bool = loop

    def GetFrames(self) -> t.Sequence['Image']:
        frame_size = (self.image.width, self.image.height / self.count)
        return tuple(self.image.crop((0, frame_size[1] * i, frame_size[0], frame_size[1] * (i + 1))) for i in range(self.count))

    class Modify_Kwargs(t.TypedDict, total=False):
        name: str
        image: 'Assets.Image | Image'
        count: int
        duration: float
        loop: bool

    def Modify(self, **kwargs: t.Unpack[Modify_Kwargs]) -> 'Animation':
        return Animation(
            kwargs.get('name', self.name),
            kwargs.get('image', self.image),
            kwargs.get('count', self.count),
            kwargs.get('duration', self.duration),
            kwargs.get('loop', self.loop),
        )

    def GetSignature(self) -> int:
        return hash(
            (
                self.name,
                self.count,
                self.duration,
                self.loop,
            )
        )

    @property
    def name(self):
        return self._name

    @property
    def image(self):
        return self._image

    @property
    def count(self):
        return self._count

    @property
    def duration(self):
        return self._duration

    @property
    def loop(self):
        return self._loop

    @property
    def size(self) -> Types.Vec2[int]:
        return Types.Vec2[int](
            self.image.width,
            self.image.height // self.count,
        )

    @property
    def frame_duration(self) -> float:
        return self.duration / self.count
