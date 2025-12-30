import typing as t
import logging
from pathlib import Path

from .Config import Config


def CreateLogger(
    name: str,
    level: int = logging.WARNING,
    terminal_level: t.Optional[int] = None,
    terminal_format: t.Optional[logging.Formatter] = None,
    file_path: t.Optional[str | Path] = None,
    file_level: t.Optional[int] = None,
    file_format: t.Optional[logging.Formatter] = None,
) -> logging.Logger:
    log = logging.Logger(name, level)

    handler = logging.StreamHandler()
    handler.setLevel(level if terminal_level is None else terminal_level)
    if terminal_format is not None:
        handler.setFormatter(terminal_format)
    log.addHandler(handler)

    if file_path is not None:
        handler = logging.FileHandler(file_path)
        handler.setLevel((level if terminal_level is None else terminal_level) if file_level is None else file_level)
        if file_format is not None or terminal_format is not None:
            handler.setFormatter(file_format if terminal_format is None else terminal_format)
        log.addHandler(handler)

    return log


core_logger = CreateLogger(
    'Core',
)
window_manager_logger = CreateLogger(
    'WindowManager',
)
asset_manager_logger = CreateLogger(
    'AssetManager',
)
input_manager_logger = CreateLogger(
    'InputManager',
)
