import typing as t
from time import perf_counter

from .. import Abc
from .Manager import Manager
from ..Core import Core
from ..Loggers import window_manager_logger
from ..Sequences import WindowSequence
from ..AsyncEvent import AsyncEvent
from ..Stopwatch import stopwatch


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

    @stopwatch
    async def Simulate(self):
        self.on_simulate.Invoke(self)

        self._simulate_time = perf_counter()

        for window in (*self.sequence,):
            window.Simulate()

        self.on_simulated.Invoke(self)

    @stopwatch
    def Register[TItem: Abc.Window](self, item: TItem) -> TItem:
        window_manager_logger.info(f'Register {item}')
        result = t.cast(TItem, super().Register(item))

        @result.on_closed
        def _(_):
            Core.window_manager.RemoveClosedWindows(True)
            
        return result

    @t.overload
    def Remove(self, item: Abc.Window, /) -> Abc.Window: ...
    @t.overload
    def Remove[TDefault: t.Any](self, item: Abc.Window, default: TDefault, /) -> Abc.Window | TDefault: ...

    @stopwatch
    def Remove(self, *args: Abc.Window | t.Any):
        window_manager_logger.info(f'Remove {t.cast(Abc.Window, args[0])}')
        return super().Remove(*args)

    def Close(self):
        self.on_close.Invoke(self)

        if self.count > 0:
            window_manager_logger.info('Close...')

            for window in (*self.sequence,):
                self.Remove(window).Close().Dispose()

            self.on_closed.Invoke(self)

    def RemoveClosedWindows(self, stop_core: bool = False):
        for window in (*self.sequence.Filter(lambda window: window.should_close),):
            self.Remove(window).Dispose()

        if stop_core and self.count == 0:
            Core.Stop()

    @property
    def sequence(self) -> WindowSequence[Abc.Window]:
        return WindowSequence(self._storage.values())

    @property
    def simulate_time(self) -> float:
        return self._simulate_time
