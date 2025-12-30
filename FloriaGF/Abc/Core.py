from abc import ABC, abstractmethod
import typing as t

if t.TYPE_CHECKING:
    from .. import Managers
    from ..TimeoutScheduler import TimeoutScheduler
    from ..Timer import TimerStorage, FixedTimer, VariableTimer
    from ..AsyncEvent import AsyncEvent


class Core(
    ABC,
):
    @property
    @abstractmethod
    def on_initialize(self) -> 'AsyncEvent[Core]':
        """Awaitable event triggered BEFORE core initialization.

        Execution blocks until ALL subscribers complete.
        """

    @property
    @abstractmethod
    def on_initialized(self) -> 'AsyncEvent[Core]':
        """Awaitable event triggered AFTER core initialization.

        Execution blocks until ALL subscribers complete.
        """

    @property
    @abstractmethod
    def on_terminate(self) -> 'AsyncEvent[Core]':
        """Awaitable event triggered BEFORE core termination.

        Execution blocks until ALL subscribers complete.
        """

    @property
    @abstractmethod
    def on_terminated(self) -> 'AsyncEvent[Core]':
        """Awaitable event triggered AFTER core termination.

        Execution blocks until ALL subscribers complete.
        """

    @property
    @abstractmethod
    def on_stop(self) -> 'AsyncEvent[Core]':
        """Non-awaitable event triggered by explicit stop request.

        Execution does not block.
        """

    @property
    @abstractmethod
    def on_simulate(self) -> 'AsyncEvent[Core]':
        '''
        Событие симуляции.

        Ожидается.
        '''

    @property
    @abstractmethod
    def on_draw(self) -> 'AsyncEvent[Core]':
        '''
        Событие отрисовки.

        Срабатывает сразу после window_manager.Simulater().

        Ожидается.
        '''

    @abstractmethod
    async def Run(self):
        """Main game loop coroutine.

        Orchestrates update cycles (simulation, rendering, scheduling) while core is enabled.
        Should handle frame pacing and exception containment.
        Typically called internally by Start().
        """

    @abstractmethod
    def Stop(self):
        """Requests graceful termination.

        Signals run loop to complete current cycle and initiate shutdown sequence.
        Triggers on_stop event immediately.
        Non-blocking - returns control before termination is complete.
        """

    @property
    @abstractmethod
    def window_manager(self) -> 'Managers.WindowManager': ...
    @window_manager.setter
    @abstractmethod
    def window_manager(self, manager: 'Managers.WindowManager'): ...

    @property
    @abstractmethod
    def asset_manager(self) -> 'Managers.AssetManager': ...
    @asset_manager.setter
    @abstractmethod
    def asset_manager(self, manager: 'Managers.AssetManager'): ...

    @property
    @abstractmethod
    def mesh_manager(self) -> 'Managers.MeshManager': ...
    @mesh_manager.setter
    @abstractmethod
    def mesh_manager(self, manager: 'Managers.MeshManager'): ...

    @property
    @abstractmethod
    def scheduler(self) -> 'TimeoutScheduler':
        """Task scheduler.

        Raises:
            RuntimeError: When accessed before Core initialization completes

        Returns:
            Initialized TimeoutScheduler instance
        """

    @scheduler.setter
    @abstractmethod
    def scheduler(self, value: 'TimeoutScheduler'): ...

    @property
    @abstractmethod
    def timer_storage(self) -> 'TimerStorage':
        """Timer registry and lifecycle manager.

        Tracks active timers (fixed/variable) and handles their cleanup.

        Raises:
            RuntimeError: When accessed before initialization completes

        Returns:
            TimerStorage instance maintaining timer collections
        """

    @timer_storage.setter
    @abstractmethod
    def timer_storage(self, value: 'TimerStorage'): ...

    @abstractmethod
    def SetExceptionCallaback(self, callback: t.Callable[[Exception], t.Any]):
        """Registers global exception handler.

        Callback receives unhandled exceptions from async contexts. Multiple calls
        override previous handlers. Default handler terminates core.

        Args:
            callback: Function accepting Exception instance. Return value ignored.
        """

    @abstractmethod
    def InvokeException(self, ex: Exception):
        """Propagates exception to global handler.

        Used internally to route exceptions through registered callback. Should be
        called for critical errors that require core shutdown.

        Args:
            ex: Exception instance to handle
        """

    @property
    @abstractmethod
    def enable(self) -> bool:
        """Core operational state flag.

        False when the kernel is halted/terminating.
        The state is controlled by the Start()/Stop() functions.
        """

    @property
    @abstractmethod
    def fps_timer(self) -> 'VariableTimer':
        """Variable-rate timer.

        Returns:
            VariableTimer instance
        """

    @property
    @abstractmethod
    def sps_timer(self) -> 'FixedTimer':
        """Fixed-rate timer.

        Returns:
            FixedTimer instance
        """

    @property
    @abstractmethod
    def tps_timer(self) -> 'VariableTimer':
        """Variable-rate timer.

        Returns:
            VariableTimer instance
        """
