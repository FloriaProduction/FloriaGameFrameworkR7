import typing as t
import functools
import math
from dataclasses import dataclass

from .Angle import Angle2D


@dataclass(frozen=True)
class Direction:
    up: bool = False
    left: bool = False
    down: bool = False
    right: bool = False

    @functools.cached_property
    def angle(self):
        return Angle2D(
            math.atan2(
                (1 if self.up else 0) + (-1 if self.down else 0),
                (1 if self.right else 0) + (-1 if self.left else 0),
            )
        )
