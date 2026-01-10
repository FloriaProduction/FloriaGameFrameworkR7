import typing as t
import glm


class Quaternion[T: t.Any = float](t.NamedTuple):
    w: T
    x: T
    y: T
    z: T

    @classmethod
    def New(cls, value: t.Iterable[T] | t.Self, /) -> t.Self:
        match len(value := tuple(value)):
            case 1:
                return cls(*((value[0],) * 4))

            case 3:
                return cls(*glm.quat(value))  # pyright: ignore[reportArgumentType]

            case 4:
                return cls(*value)

            case _:
                raise
