import typing as t

from FloriaGF import Managers, AsyncEvent, Abc
from FloriaGF.Managers.Input import Actions, hints


on_setup = AsyncEvent[Managers.Input.InputManager]()
'''Вызывается после настройки input_manager'''
on_clear = AsyncEvent[Managers.Input.InputManager]()
'''Вызывается после очистки input_manager'''

on_load = AsyncEvent[Managers.Input.InputManager]()
'''Вызывается при загрузке модуля, после настройки input_manager'''
on_unload = AsyncEvent[Managers.Input.InputManager]()
'''Вызывается при выгрузке модуля, перед очисткой input_manager'''


from . import Window


def Setup(input_manager: Managers.Input.InputManager):
    on_setup.Invoke(input_manager)


def Clear(input_manager: Managers.Input.InputManager):
    on_clear.Invoke(input_manager)


@Window.on_setup.Register
def _(window: Abc.Window):
    Setup(window.input_manager)


@Window.on_clear.Register
def _(window: Abc.Window):
    Clear(window.input_manager)
