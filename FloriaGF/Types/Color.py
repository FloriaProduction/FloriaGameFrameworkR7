import typing as t


class RGB[T: t.Any = int](t.NamedTuple):
    r: T
    g: T
    b: T

    @t.overload
    @classmethod
    def New(cls, value: tuple[T, T, T] | t.Self | t.Iterable[T], /) -> t.Self: ...
    @t.overload
    @classmethod
    def New(cls, value: T, /) -> t.Self: ...

    @classmethod
    def New(cls, value: t.Iterable[T] | T | t.Self) -> t.Self:
        return cls(*value) if isinstance(value, t.Iterable) else cls(value, value, value)

    def ToRGBA(self, a: T) -> 'RGBA[T]':
        return RGBA(*self, a)


class RGBA[T: t.Any = int](t.NamedTuple):
    r: T
    g: T
    b: T
    a: T

    @t.overload
    @classmethod
    def New(cls, value: tuple[T, T, T, T] | t.Self | t.Iterable[T], /) -> t.Self: ...
    @t.overload
    @classmethod
    def New(cls, value: T, /) -> t.Self: ...

    @classmethod
    def New(cls, value: t.Iterable[T] | T | t.Self) -> t.Self:
        return cls(*value) if isinstance(value, t.Iterable) else cls(value, value, value, value)

    def ToRGB(self) -> 'RGB[T]':
        return RGB(self.r, self.g, self.b)
