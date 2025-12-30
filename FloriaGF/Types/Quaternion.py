import typing as t
import pyrr
import numpy as np


class Quaternion[T: t.Any = float](t.NamedTuple):
    x: T
    y: T
    z: T
    w: T

    @classmethod
    def New(cls, value: t.Iterable[T] | t.Self | pyrr.Quaternion, /) -> t.Self:
        return (
            cls(*value)
            if isinstance(value, pyrr.Quaternion)
            else cls(*pyrr.quaternion.create_from_eulers(value, dtype=np.float32))
        )
