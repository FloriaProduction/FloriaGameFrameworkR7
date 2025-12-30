import typing as t
import pyrr


class Vec2[T: t.Any](t.NamedTuple):
    x: T
    y: T

    @property
    def width(self):
        return self.x

    @property
    def height(self):
        return self.y

    @t.overload
    @classmethod
    def New(cls, value: T, /) -> t.Self: ...
    @t.overload
    @classmethod
    def New(cls, value: tuple[T, T] | t.Iterable[T], /) -> t.Self: ...

    @classmethod
    def New(cls, value: t.Iterable[T] | T) -> t.Self:
        return cls(*value) if isinstance(value, t.Iterable) else cls(value, value)

    def ToVec3(self, z: T) -> 'Vec3[T]':
        return Vec3(*self, z)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'Vec2<{id(self)}>(x: {self.x:.6f}, y: {self.y:.6f})'


class Vec3[T: t.Any](t.NamedTuple):
    x: T
    y: T
    z: T

    @property
    def width(self):
        return self.x

    @property
    def height(self):
        return self.y

    @property
    def depth(self):
        return self.z

    @t.overload
    @classmethod
    def New(cls, value: T, /) -> t.Self: ...
    @t.overload
    @classmethod
    def New(cls, value: tuple[T, T, T] | t.Self | pyrr.Vector3 | t.Iterable[T], /) -> t.Self: ...

    @classmethod
    def New(cls, value: pyrr.Vector3 | t.Iterable[T] | T) -> t.Self:
        return (
            cls(*value.tolist())
            if isinstance(value, pyrr.Vector3)
            else cls(*value) if isinstance(value, t.Iterable) else cls(value, value, value)
        )

    def ToVec2(self, exclude_index: t.Literal[0, 1, 2]) -> Vec2[T]:
        return Vec2(*(x for i, x in enumerate(self) if i != exclude_index))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'Vec3<{id(self)}>(x: {self.x:.6f}, y: {self.y:.6f}, z: {self.z:.6f})'
