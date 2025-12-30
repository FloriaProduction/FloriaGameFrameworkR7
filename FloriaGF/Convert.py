import typing as t
from uuid import UUID
import pathlib
import numpy as np
from OpenGL import GL
import functools

from .Config import Config
from . import Types


def ToUUID(value: str | UUID) -> UUID:
    if isinstance(value, str):
        value = UUID(value)
    return value


def ToPath(value: str | pathlib.Path) -> pathlib.Path:
    if not isinstance(value, pathlib.Path):
        value = pathlib.Path(value)
    return value


@t.overload
def ToPIX(data: Types.Vec3[Types.hints.number], /) -> Types.Vec3[Types.hints.number]: ...


@t.overload
def ToPIX(data: Types.Vec2[Types.hints.number], /) -> Types.Vec2[Types.hints.number]: ...


@t.overload
def ToPIX(data: t.Iterable[Types.hints.number], /) -> tuple[Types.hints.number, ...]: ...


def ToPIX(
    data: Types.Vec3[Types.hints.number] | Types.Vec2[Types.hints.number] | t.Iterable[Types.hints.number],
):
    '''
    Конвертировать мировые координаты в пиксели
    '''
    new_data = (x * Config.PIX_scale for x in data)
    if isinstance(data, Types.Vec2 | Types.Vec3):
        return data.New(new_data)
    return tuple(new_data)


@t.overload
def FromPIX[T: float | int](data: T, /) -> T: ...


@t.overload
def FromPIX[T: float | int](data: Types.Vec3[T], /) -> Types.Vec3[T]: ...


@t.overload
def FromPIX[T: float | int](data: Types.Vec2[T], /) -> Types.Vec2[T]: ...


@t.overload
def FromPIX[T: float | int](data: t.Iterable[T], /) -> tuple[T, ...]: ...


def FromPIX(
    data: Types.Vec3[float | int] | Types.Vec2[float | int] | t.Iterable[float | int] | float | int,
):
    '''
    Конвертировать пиксели в мировые координаты
    '''

    if isinstance(data, float | int):
        return data / Config.PIX

    new_data = (x / Config.PIX for x in data)
    if isinstance(data, Types.Vec2 | Types.Vec3):
        return data.New(new_data)
    return tuple(new_data)
