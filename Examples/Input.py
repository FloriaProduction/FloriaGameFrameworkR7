import typing as t

from FloriaGF import Managers, AsyncEvent, Abc


on_setup = AsyncEvent[Managers.Input.InputManager]()
on_clear = AsyncEvent[Managers.Input.InputManager]()


from . import Window


def Get() -> Managers.Input.InputManager:
    return Window.Get().input_manager


def Setup(input_manager: Managers.Input.InputManager):
    on_setup.Invoke(input_manager)


def Clear(input_manager: Managers.Input.InputManager):
    on_clear.Invoke(input_manager)


@Window.on_setup
def _(window: Abc.Window):
    Setup(window.input_manager)


@Window.on_clear
def _(window: Abc.Window):
    Clear(window.input_manager)
