import glfw
import typing as t
import functools
import itertools
import inspect
import asyncio
import pathlib
import re
import pydoc
import numpy as np
from OpenGL import GL
from contextlib import contextmanager
import math
import glm

if t.TYPE_CHECKING:
    from . import Types, Protocols


T = t.TypeVar('T')


def Coalesce[T: t.Any, TDefault: t.Optional[t.Any]](data: t.Iterable[t.Optional[T]], default: TDefault = None) -> T | TDefault:
    for item in data:
        if item is None:
            continue
        return item
    return default


def CoalesceLazy[T: t.Any, T2: t.Any](item0: t.Optional[T], item1: t.Callable[[], T2]) -> T | T2:
    if item0 is None:
        return item1()
    return item0


def IncludeIfExists[TValue: t.Any](
    data_from: dict[str, TValue],
    key_from: str,
    data_to: dict[str, TValue],
    key_to: t.Optional[str] = None,
    func: t.Callable[[TValue], TValue] = lambda value: value,
) -> dict[str, TValue]:
    '''
    Args:
        data_from - словарь, в котором проверяется наличие ключа key
        data_to - словарь, в который добавляется значение по ключу key (или key_to, если дан)
        func - функция преобразования
    '''

    if key_from in data_from:
        data_to[key_from if key_to is None else key_to] = func(data_from[key_from])
    return data_to


async def CoalesceLazyAsync[T: t.Any, T2: t.Any](
    item0: t.Optional[T], item1: t.Callable[[], t.Coroutine[t.Any, t.Any, T2]]
) -> T | T2:
    if item0 is None:
        return await item1()
    return item0


async def WaitCors[T](
    cors: t.Union[t.Iterable[t.Coroutine[t.Any, t.Any, T]], t.AsyncIterable[t.Coroutine[t.Any, t.Any, T]]],
) -> list[T]:
    return await asyncio.gather(*(cors if isinstance(cors, t.Iterable) else [cor async for cor in cors]))


async def WaitFuncCors[T](
    cor: t.Coroutine[t.Any, t.Any, T] | T,
) -> T:
    if isinstance(cor, t.Coroutine):
        return await cor  # pyright: ignore[reportUnknownVariableType]
    return cor


async def YieldEvery[T: t.Any](
    items: t.Iterable[T],
    *,
    step: int = 100,
    pause: float = 0,
    progress_callback: t.Optional[t.Callable[[int, T], t.Coroutine[t.Any, t.Any, t.Any] | t.Any]] = None,
) -> t.AsyncIterable[T]:
    """
    Асинхронно перебирает элементы с периодическими паузами для кооперативной многозадачности.

    Эта функция позволяет обрабатывать большие коллекции данных, периодически
    отдавая управление другим асинхронным задачам, что предотвращает блокировку
    event_loop и улучшает отзывчивость приложения.

    Args:
        items: Итерируемая коллекция элементов для обработки
        step: Количество элементов между паузами.
        pause: Длительность паузы в секундах. Может быть 0 для минимального переключения контекста.
        progress_callback: Функция, вызываемая для каждого элемента с его индексом.

    Yields:
        T: Очередной элемент из коллекции.

    Raises:
        ValueError: Если `step` отрицательное или ровно нулю.

    Example::

        # Базовое использование
        async for item in YieldEvery(range(100), step=10):
            process(item)

        # С обработкой прогресса
        async for item in YieldEvery(data, progress_callback=lambda i, x: print(f"Обработано: {i / len(data)}%")):
            await process_async(item)
    """

    if step <= 0:
        raise ValueError(f"Step must be non-negative, got {step}")

    for i, item in enumerate(items):
        yield item

        if progress_callback is not None:
            await Invoke(progress_callback, i, item)

        if step > 0 and i % step == 0:
            await asyncio.sleep(pause)


def RemoveKeys(data: dict[str, t.Any], *keys: str) -> dict[str, t.Any]:
    return {key: value for key, value in data.items() if key not in keys}


def ComparePath(path1: Types.hints.path, path2: Types.hints.path) -> bool:
    if isinstance(path1, str):
        path1 = pathlib.Path(path1)
    if isinstance(path2, str):
        path2 = pathlib.Path(path2)

    return path1.parent.resolve().joinpath(path1.name) == path2.parent.resolve().joinpath(path2.name)


def DirectoryContainsFile(dir: Types.hints.path, file: Types.hints.path) -> bool:
    if isinstance(dir, str):
        dir = pathlib.Path(dir)
    if isinstance(file, str):
        file = pathlib.Path(file)

    return file.resolve().is_relative_to(dir.resolve())


def ReplaceTemplates(text: str, replacements: dict[str, t.Any], safe: bool = False) -> str:
    return re.sub(
        r'\{ *(\w+) *\}',
        lambda m: str(replacements.get(m.group(1), '?') if safe else replacements[m.group(1)]),
        text,
    )


def Smooth(
    value_1: float,
    value_2: float,
    k: float,
    min: float = 0.0001,
):
    result = value_1 + (value_2 - value_1) * k
    if abs(value_2 - result) <= min:
        return value_2
    return result


# def SmoothIter(
#     iter_1: t.Iterable[float],
#     iter_2: t.Iterable[float],
#     k: float,
#     min: float = 0.0001,
# ) -> t.Iterable[float]:
#     return itertools.starmap(
#         lambda x, y: Smooth(x, y, k, min),
#         zip(iter_1, iter_2, strict=True),
#     )


def SmoothIter(
    i1: t.Iterable[float],
    i2: t.Iterable[float],
    k: float,
    min: float = 0.0001,
) -> t.Iterable[float]:
    """
    Линейная интерполяция между двумя итерируемыми последовательностями чисел.

    Args:
        i1: Первая последовательность чисел
        i2: Вторая последовательность чисел
        k: Коэффициент интерполяции от 0.0 до 1.0
        min: Минимальное различие для завершения интерполяции

    Returns:
        Интерполированные значения

    Raises:
        ValueError: Если последовательности разной длины
    """
    return map(
        lambda item: Smooth(item[0], item[1], k, min),
        zip(i1, i2, strict=True),
    )


def Slerp(
    q1: 'Types.Quaternion[float] | tuple[float, float, float, float]',
    q2: 'Types.Quaternion[float] | tuple[float, float, float, float]',
    k: float,
) -> tuple[float, float, float, float]:
    """
    Сферическая линейная интерполяция (SLERP) между двумя кватернионами.

    Args:
        q1: Начальный кватернион
        q2: Конечный кватернион
        k: Параметр интерполяции от 0.0 до 1.0

    Returns:
        Интерполированный кватернион: w x y z

    Raises:
        ValueError: Если кватернионы не нормализованы
    """

    return glm.slerp(q1, q2, k).to_tuple()


def Distance2D(val1: tuple[float, float], val2: tuple[float, float]) -> float:
    return math.sqrt((val1[0] - val2[0]) ** 2 + (val1[1] - val2[1]) ** 2)


def Distance3D(val1: tuple[float, float, float], val2: tuple[float, float, float]) -> float:
    return math.sqrt((val1[0] - val2[0]) ** 2 + (val1[1] - val2[1]) ** 2 + (val1[2] - val2[2]) ** 2)


def FirstOrDefault[T: t.Any, TDefault: t.Optional[t.Any]](data: t.Iterable[T], default: TDefault = None) -> T | TDefault:
    for item in data:
        return item
    return default


def GetClassAttrib[TDefault: t.Optional[t.Any]](cls: type, name: str, default: TDefault = None) -> t.Optional[t.Any | TDefault]:
    for base in (base for base in cls.mro() if base is not object):
        if (value := base.__dict__.get(name)) is not None:
            return value
    return default


class _InvokeFunc[T](t.Protocol):
    def __call__(self, *args: t.Any, **kwds: t.Any) -> T | t.Coroutine[t.Any, t.Any, T]: ...


async def Invoke[T: t.Any](func: _InvokeFunc[T], *args: t.Any, **kwargs: t.Any) -> T:
    result = func(*args, **kwargs)
    if isinstance(result, t.Coroutine):
        return t.cast(T, await result)
    return result


@contextmanager
def EmptyBind[T: t.Optional[t.Any]](item: T = None) -> t.Generator[T, t.Any, None]:
    yield item


@contextmanager
def ExceptionHandler(handler: t.Optional[t.Callable[[Exception], t.Any]] = None):
    try:
        yield

    except Exception as ex:
        if handler is not None:
            handler(ex)
        else:
            raise
