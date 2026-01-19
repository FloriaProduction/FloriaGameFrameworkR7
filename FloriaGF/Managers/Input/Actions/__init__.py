import typing as t

from .Action import Action, ActionHandler, KeyboardHandler
from .PressHandler import PressAction, PressHandler


actions = t.Union[
    Action,
    PressAction,
]
