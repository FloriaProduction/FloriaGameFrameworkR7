import typing as t
import asyncio
import OpenGL
import os

os.chdir(os.path.dirname(f'{os.path.abspath(__file__)}'))
OpenGL.ERROR_CHECKING = False

from FloriaGF import (
    Core,
)

import Game


@Core.on_initialized.Register
async def _(_):
    await Game.Window.Load()


@Core.on_terminate.Register
async def _(_):
    await Game.Window.Unload()


if __name__ == '__main__':
    asyncio.run(Core.Run())
