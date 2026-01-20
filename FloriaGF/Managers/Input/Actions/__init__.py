import typing as t

from .Base import Action, ActionHandler, KeyboardHandler

from .KeyPress import KeyPressAction, ValidateKeyPressAction, KeyPressHandler
from .KeyState import KeyStateAction, ValidateKeyStateAction, KeyStateHandler

if t.TYPE_CHECKING:
    from .. import hints


actions = t.Union[
    Action,
    KeyPressAction,
    KeyStateAction,
]

action_validators: dict[hints.action_type, t.Callable[[Action], bool]] = {
    'press': ValidateKeyPressAction,
    'state': ValidateKeyStateAction,
}
