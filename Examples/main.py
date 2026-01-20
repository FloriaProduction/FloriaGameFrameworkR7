import typing as t
import asyncio
import OpenGL

OpenGL.ERROR_CHECKING = False
import os

os.chdir(os.path.dirname(f'{os.path.abspath(__file__)}'))

from FloriaGF import (
    Core,
    Config,
)
from FloriaGF.Managers import ModuleManager

import Game


@Core.on_initialized
async def _(_):
    await ModuleManager.Load(
        Game.Window,
    )

@Core.on_terminate
async def _(_):
    await ModuleManager.Unload(
        Game.Window,
    )


if __name__ == '__main__':
    Config.FPS = 300
    Config.SPS = 20
    Config.VSYNC = 'full'

    asyncio.run(Core.Run())
