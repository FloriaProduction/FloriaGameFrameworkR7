"""Менеджер для управления модулями."""

import typing as t
import types as ts

from .. import Utils
from ..Loggers import module_manager_logger


async def Processing(
    modules_or_coros: t.Iterable[ts.ModuleType | t.Awaitable[t.Any] | t.Callable[[], t.Any | t.Awaitable[t.Any]]],
    method_name: t.Literal['Load', 'Unload'] | str,
):
    for moc in modules_or_coros:
        if isinstance(moc, ts.ModuleType):
            if (func := getattr(moc, method_name, None)) is not None:
                await Utils.Invoke(func)

            else:
                module_manager_logger.warning(f'Модуль "{moc}" не имеет метода "{method_name}"')

        elif isinstance(moc, t.Awaitable):
            await moc

        else:
            await Utils.Invoke(moc)


async def Load(
    *modules_or_coros: ts.ModuleType | t.Awaitable[t.Any] | t.Callable[[], t.Any | t.Awaitable[t.Any]],
    method_name: t.Literal['Load', 'Unload'] | str = 'Load',
):
    """Загружает один или несколько модулей, вызывает функции, либо ожидает завершения корутин.

    Args:
        *modules_or_coros (ts.ModuleType | t.Awaitable[t.Any]): Переменное количество модулей или корутин.
        method_name (t.Literal['Load', 'Unload'] | str, optional): Название вызываемого метода модуля. По умолчанию 'Load'.

    Example::

        await Load(
            Module1,
            Module2.AsyncFunc(),
        )
    """
    await Processing(modules_or_coros, method_name)


async def Unload(
    *modules_or_coros: ts.ModuleType | t.Awaitable[t.Any] | t.Callable[[], t.Any | t.Awaitable[t.Any]],
    method_name: t.Literal['Load', 'Unload'] | str = 'Unload',
):
    """Выгружает один или несколько модулей, вызывает функции, либо ожидает завершения корутин.

    Args:
        *modules_or_coros (ts.ModuleType | t.Awaitable[t.Any]): Переменное количество модулей или корутин.
        method_name (t.Literal['Load', 'Unload'] | str, optional): Название вызываемого метода модуля. По умолчанию 'Unload'.

    Example::

        await Unload(
            Module1,
            Module2.AsyncFunc(),
        )
    """
    await Processing(modules_or_coros, method_name)
