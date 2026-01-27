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
        '_start',
        '_duration',
        '_loop',
        '_orientation',
        '_points',
    )

    def __init__(
        self,
        name: str,
        image: 'Assets.Image | Image',
        count: t.Optional[int] = None,
        start: t.Optional[int] = None,
        duration: t.Optional[float] = None,
        loop: t.Optional[bool] = None,
        orientation: t.Optional[Types.hints.orientation] = None,
        points: t.Optional[t.Mapping[int, t.Mapping['Animation.POINT_NAME', Types.hints.offset_2d]]] = None,
    ):
        super().__init__()

        self._name: str = name
        self._image: 'Image' = image if isinstance(image, Image) else Validator.NotNone(image.image)
        self._count: int = 1 if count is None else count
        if not self._count.is_integer() or self._count < 1:
            raise
        self._duration: float = 0 if duration is None else duration
        if self._duration < 0:
            raise
        self._loop: bool = False if loop is None else loop
        self._orientation: Types.hints.orientation = 'horizontal' if orientation is None else orientation
        self._points: t.Mapping[int, t.Mapping[Animation.POINT_NAME, Types.Vec2[int]]] = (
            {}
            if points is None
            else {frame: {name: Types.Vec2[int].New(offset) for name, offset in data.items()} for frame, data in points.items()}
        )
        self._start: int = 0 if start is None else start

    def GetTexture(self, window: Abc.Window) -> Texture:
        if (texture_arrays := self._texture_arrays.get(window.id)) is None:
            texture_arrays = TextureArrays()
            self._texture_arrays[window.id] = texture_arrays

            @window.on_closed
            def _(window: Abc.Window):
                self._texture_arrays.pop(window.id, None)

        if (texture := texture_arrays.Get(self)) is None:
            texture = texture_arrays.Register(self, window)

        return texture

    def GetFrames(self) -> t.Sequence['Image']:
        frame_size = self.frame_size

        return tuple(
            self.image.crop(
                (0, frame_size[1] * i, frame_size[0], frame_size[1] * (i + 1))
                if self.orientation == 'vertical'
                else (
                    frame_size[0] * i,
                    0,
                    frame_size[0] * (i + 1),
                    frame_size[1],
                )
            )
            for i in range(self.count)
        )

    class Modify_Kwargs(t.TypedDict, total=False):
        name: str
        image: 'Assets.Image | Image'
        count: int
        duration: float
        loop: bool
        orientation: Types.hints.orientation
        points: t.Mapping[int, t.Mapping['Animation.POINT_NAME', Types.hints.offset_2d]]
        start: int

    def Modify(self, **kwargs: t.Unpack[Modify_Kwargs]) -> 'Animation':
        return Animation(
            kwargs.get('name', self.name),
            kwargs.get('image', self.image),
            kwargs.get('count', self.count),
            kwargs.get('start', self.start),
            kwargs.get('duration', self.duration),
            kwargs.get('loop', self.loop),
            kwargs.get('orientation', self.orientation),
            kwargs.get('points', self.points),
        )

    def GetSignature(self) -> int:
        # TODO: пересмотреть сигнатуры
        return hash(
            (
                self.name,
                self.count,
                self.duration,
                self.loop,
            )
        )

    @t.overload
    def GetPoint(
        self,
        name: 'Animation.POINT_NAME',
        frame: int = 0,
        /,
    ) -> Types.Vec2[int]: ...

    @t.overload
    def GetPoint[TDefault: t.Optional[t.Any]](
        self,
        name: 'Animation.POINT_NAME',
        frame: int = 0,
        default: TDefault = None,
        /,
    ) -> Types.Vec2[int] | TDefault: ...

    @functools.lru_cache
    def GetPoint(self, *args: 'Animation.POINT_NAME | int | t.Any'):
        name = t.cast('Animation.POINT_NAME', args[0])
        frame = t.cast(int, args[1]) if len(args) >= 2 else 0
        if frame < 0 or frame >= self.count:
            raise

        for _, data in (*filter(lambda item: item[0] <= frame, self._points.items()),)[::-1]:
            if (offset := data.get(name)) is not None:
                return offset
        return args[2] if len(args) >= 3 else Types.Vec2[int](0, 0)

    @property
    def name(self):
        return self._name

    @property
    def image(self):
        return self._image

    @property
    def count(self):
        '''[1, ...)'''
        return self._count

    @property
    def start(self):
        return self._start

    @property
    def duration(self):
        '''[0, ...)'''
        return self._duration

    @property
    def loop(self):
        return self._loop

    @property
    def orientation(self):
        return self._orientation

    @property
    def size(self) -> Types.Vec2[int]:
        return Types.Vec2[int](
            self.image.width,
            self.image.height // self.count,
        )

    @property
    def frame_size(self) -> Types.Vec2[int]:
        '''
        Example::

            Vec2[int](
                [1, ...),
                [1, ...),
            )
        '''
        return Types.Vec2[int].New(
            (self.image.width, self.image.height // self.count)
            if self.orientation == 'vertical'
            else (self.image.width // self.count, self.image.height)
        )

    @property
    def frame_duration(self) -> float:
        '''[0, ...)'''
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
                self.start,
                self.duration,
                self.loop,
                self.orientation,
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
