import typing as t
import math
import functools

from .Vec import Vec2


class Angle2D(t.NamedTuple):
    angle: t.Optional[float]

    @functools.cached_property
    def vec2(self) -> Vec2[float]:
        return (
            Vec2[float](0, 0)
            if self.angle is None
            else Vec2(
                math.cos(self.angle),
                math.sin(self.angle),
            )
        )
