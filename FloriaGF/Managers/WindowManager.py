import typing as t
from time import perf_counter
import asyncio

from .. import Abc, Utils
from .Manager import Manager
from ..Timer import VariableTimer
from ..Core import Core
from ..Config import Config
from ..Loggers import window_manager_logger
from ..Sequences import WindowSequence
from ..AsyncEvent import AsyncEvent
from ..Stopwatch import Stopwatch


class WindowManager(
    Manager[Abc.Graphic.Windows.Window],
    Abc.Mixins.SimulatableAsync,
):
    __slots__ = (
        '_simulate_time',
        '_on_simulate',
        '_on_simulated',
        '_on_close',
        '_on_closed',
    )

    @property
    def on_simulate(self) -> AsyncEvent['WindowManager']:
        return self._on_simulate

    @property
    def on_simulated(self) -> AsyncEvent['WindowManager']:
        return self._on_simulated

    @property
    def on_close(self) -> AsyncEvent['WindowManager']:
        return self._on_close

    @property
    def on_closed(self) -> AsyncEvent['WindowManager']:
        return self._on_closed

    def __init__(self) -> None:
        super().__init__()

        self._simulate_time = perf_counter()

        self._on_simulate = AsyncEvent['WindowManager']()
        self._on_simulated = AsyncEvent['WindowManager']()
        self._on_close = AsyncEvent['WindowManager']()
        self._on_closed = AsyncEvent['WindowManager']()

        self._stopwatch_Simulate = Stopwatch()
        self._stopwatch_Register = Stopwatch()
        self._stopwatch_Remove = Stopwatch()

    @t.final
    async def Simulate(self):
        with self._stopwatch_Simulate:
            self.on_simulate.Invoke(self)

            self._simulate_time = perf_counter()

            for window in self.sequence:
                window.Simulate()

            self.on_simulated.Invoke(self)

    def Register[TItem: Abc.Graphic.Windows.Window](self, item: TItem) -> TItem:
        with self._stopwatch_Register:
            window_manager_logger.info(f'Register {item}')
            result = t.cast(TItem, super().Register(item))

            @result.on_closed.Register
            async def _(window: Abc.Graphic.Windows.Window):
                await self._RemoveClosedWindows()
                if self.count == 0:
                    Core.Stop()

            return result

    def Remove(self, *args: Abc.Window | t.Any):
        with self._stopwatch_Remove:
            window_manager_logger.info(f'Remove {t.cast(Abc.Window, args[0])}')
            return super().Remove(*args)

    def Close(self):
        self.on_close.Invoke(self)

        if self.count > 0:
            window_manager_logger.info('Close...')

            for window in (*self.sequence,):
                self.Remove(window).Close().Dispose()

            self.on_closed.Invoke(self)

    async def _RemoveClosedWindows(self):
        for window in (*self.sequence.Filter(lambda window: window.should_close),):
            self.Remove(window).Dispose()

    @property
    def sequence(self) -> WindowSequence[Abc.Window]:
        return WindowSequence(self._storage.values())

    @property
    def simulate_time(self) -> float:
        return self._simulate_time
