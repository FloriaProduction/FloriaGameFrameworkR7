import typing as t
from PIL.Image import Image
import functools
from uuid import UUID

from FloriaGF import Abc, Types, Validator
from FloriaGF.Graphic.Objects.Texture import Texture

from ..Graphic.Objects.TextureArrays import TextureArrays

if t.TYPE_CHECKING:
    from FloriaGF import Assets


class Animation(Abc.Mixins.Signaturable, Abc.Mixins.Repr):
    # Window.id: TextureArrays
    _texture_arrays: dict[UUID, TextureArrays] = {}

    POINT_NAME = t.Union[t.Literal['origin'], str]

    __slots__ = (
        '_name',
        '_image',
        '_count',
        '_duration',
        '_loop',
        '_points',
    )

    def __init__(
        self,
        name: str,
        image: 'Assets.Image | Image',
        count: int = 1,
        duration: float = 0,
        loop: bool = False,
        points: t.Mapping[int, t.Mapping['Animation.POINT_NAME', Types.hints.offset_2d]] = {},
    ):
        super().__init__()

        self._name: str = name
        self._image: 'Image' = image if isinstance(image, Image) else Validator.NotNone(image.image)
        self._count: int = count
        self._duration: float = duration
        self._loop: bool = loop
        self._points: t.Mapping[int, t.Mapping[Animation.POINT_NAME, Types.Vec2[int]]] = {
            frame: {name: Types.Vec2[int].New(offset) for name, offset in data.items()} for frame, data in points.items()
        }

    def GetTexture(self, window: Abc.Window) -> Texture:
        if (texture_arrays := self._texture_arrays.get(window.id)) is None:
            texture_arrays = TextureArrays()
            self._texture_arrays[window.id] = texture_arrays

            @window.on_closed.Register
            def _(window: Abc.Window):
                self._texture_arrays.pop(window.id, None)

        if (texture := texture_arrays.Get(self)) is None:
            texture = texture_arrays.Register(self, window)

        return texture

    def GetFrames(self) -> t.Sequence['Image']:
        frame_size = (self.image.width, self.image.height / self.count)
        return tuple(self.image.crop((0, frame_size[1] * i, frame_size[0], frame_size[1] * (i + 1))) for i in range(self.count))

    class Modify_Kwargs(t.TypedDict, total=False):
        name: str
        image: 'Assets.Image | Image'
        count: int
        duration: float
        loop: bool
        points: t.Mapping[int, t.Mapping['Animation.POINT_NAME', Types.hints.offset_2d]]

    def Modify(self, **kwargs: t.Unpack[Modify_Kwargs]) -> 'Animation':
        return Animation(
            kwargs.get('name', self.name),
            kwargs.get('image', self.image),
            kwargs.get('count', self.count),
            kwargs.get('duration', self.duration),
            kwargs.get('loop', self.loop),
            kwargs.get('points', self.points),
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

    @functools.lru_cache
    def GetPoint(self, name: 'Animation.POINT_NAME', frame: int = 0) -> Types.Vec2[int]:
        offset: t.Optional[Types.Vec2[int]] = None

        for _, data in (*filter(lambda item: item[0] <= frame, self._points.items()),)[::-1]:
            if (offset := data.get(name)) is not None:
                break

        if offset is None:
            return Types.Vec2[int].New(0)
        return offset

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

    @property
    def points(self):
        return self._points

    def _GetStrKwargs(self) -> dict[str, t.Any]:
        return {
            **super()._GetStrKwargs(),
            'name': f'"{self.name}"',
            'count': self.count,
            'dur': self.duration,
        }

    def __hash__(self) -> int:
        return hash(
            (
                self.name,
                self.image.size,
                self.count,
                self.duration,
                self.loop,
                tuple(
                    tuple(
                        (
                            frame,
                            tuple(
                                (
                                    name,
                                    offset,
                                )
                                for name, offset in data.items()
                            ),
                        )
                    )
                    for frame, data in self.points.items()
                ),
            )
        )

    def __eq__(self, other: t.Any) -> bool:
        if not isinstance(other, Animation):
            return False
        return self.__hash__() == other.__hash__()
