import typing as t

from ..Config import Config

_depth: int = 0


def Print(text: str):
    if Config.SHOW_SWITCHER_OUTPUT:
        print(f'{'. ' * _depth}{text}')


def OutPut(name: str, action: str, inc: bool, item: t.Any):
    global _depth

    if not inc:
        _depth -= 1

    Print(f'{action} {name}: {item}')

    if inc:
        _depth += 1
