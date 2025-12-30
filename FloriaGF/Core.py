import glfw
import asyncio
import typing as t
from time import perf_counter

from . import Abc, Utils, Validator
from .Config import Config
from .Loggers import core_logger
from .TimeoutScheduler import TimeoutScheduler
from .Timer import TimerStorage, VariableTimer, FixedTimer
from .AsyncEvent import AsyncEvent
from .Stopwatch import Stopwatch

if t.TYPE_CHECKING:
    from . import Managers


class CoreCls(Abc.Core):
    def __init__(self) -> None:
        super().__init__()

        self._enable: bool = True

        self._window_manager: t.Optional['Managers.WindowManager'] = None
        self._asset_manager: t.Optional['Managers.AssetManager'] = None
        self._mesh_manager: t.Optional['Managers.MeshManager'] = None

        self._scheduler: t.Optional[TimeoutScheduler] = None
        self._timer_storage: t.Optional[TimerStorage] = None

        self._exception_callback: t.Optional[t.Callable[[Exception], t.Any]] = self._ExceptionCallback

        self._on_initialize = AsyncEvent[Abc.Core]()
        self._on_initialized = AsyncEvent[Abc.Core]()
        self._on_terminate = AsyncEvent[Abc.Core]()
        self._on_terminated = AsyncEvent[Abc.Core]()
        self._on_stop = AsyncEvent[Abc.Core]()
        self._on_stoped = AsyncEvent[Abc.Core]()

        self._on_simulate = AsyncEvent[Abc.Core]()
        self._on_draw = AsyncEvent[Abc.Core]()

        self._fps_timer: t.Optional[VariableTimer] = None
        self._sps_timer: t.Optional[FixedTimer] = None
        self._tps_timer: t.Optional[VariableTimer] = None

        self._stopwatch_cycle = Stopwatch()
        '''Доступно только при `Config.GAME_CYCLE_MODE = 'sync'`'''

    def _ExceptionCallback(self, ex: Exception):
        core_logger.error('', exc_info=True)
        self.Stop()

    async def Initialize(self):
        core_logger.info('Initialize...')
        t1 = perf_counter()

        from . import Managers

        await self.on_initialize.InvokeAsync(self)

        glfw.init()

        self._window_manager = Utils.CoalesceLazy(self._window_manager, lambda: Managers.WindowManager())
        self._asset_manager = Utils.CoalesceLazy(self._asset_manager, lambda: Managers.AssetManager())
        self._mesh_manager = Utils.CoalesceLazy(self._mesh_manager, lambda: Managers.MeshManager())

        self._scheduler = Utils.CoalesceLazy(self._scheduler, lambda: TimeoutScheduler())
        self._timer_storage = Utils.CoalesceLazy(self._timer_storage, lambda: TimerStorage())

        await self.on_initialized.InvokeAsync(self)

        self._fps_timer = VariableTimer(Config.FPS_delay)
        self._sps_timer = FixedTimer(Config.SPS_delay)
        self._tps_timer = VariableTimer(Config.TPS_delay)

        core_logger.info(f'Initialized for {perf_counter() - t1:.4f} sec')

    @staticmethod
    async def _AllTasksCancel():
        current_task = asyncio.current_task()
        if current_task is None:
            return

        tasks_to_cancel = [task for task in asyncio.all_tasks() if task is not current_task]

        if len(tasks_to_cancel) == 0:
            return

        for task in tasks_to_cancel:
            task.cancel()

        await asyncio.wait(tasks_to_cancel, timeout=Config.CANCEL_TASK_TIMEOUT)

    async def Terminate(self):
        core_logger.info('Terminate...')
        t1 = perf_counter()

        await self.on_terminate.InvokeAsync(self)

        await self._AllTasksCancel()

        self.window_manager.Close()

        self.window_manager.Dispose()
        self.asset_manager.Dispose()
        self.mesh_manager.Dispose()

        glfw.terminate()

        await self.on_terminated.InvokeAsync(self)

        core_logger.info(f'Terminated for {perf_counter() - t1:.4f} sec')

    async def Run(self):
        await self.Initialize()

        try:
            match Config.GAME_CYCLE_MODE:
                case 'concurent':

                    async def RunWindowManager():
                        while self.enable:
                            if self.fps_timer.Try():
                                glfw.poll_events()
                                await self.window_manager.Simulate()
                                await self.on_draw.InvokeAsync(self)
                            await asyncio.sleep(0)

                    async def RunSimulateManager():
                        while self.enable:
                            if self.sps_timer.Try():
                                await self.on_simulate.InvokeAsync(self)
                            await asyncio.sleep(0)

                    async def RunTimers():
                        while self.enable:
                            # if self.tps_timer.Try():
                            # await self.timer_storage.Invoke()
                            await asyncio.sleep(0)

                    await Utils.WaitCors((RunWindowManager(), RunSimulateManager(), RunTimers()))

                case 'sync':
                    while self.enable:
                        with self._stopwatch_cycle:
                            if self.fps_timer.Try():
                                glfw.poll_events()
                                await self.window_manager.Simulate()
                                await self.on_draw.InvokeAsync(self)

                            if self.sps_timer.Try():
                                await self.on_simulate.InvokeAsync(self)

                            # if self.tps_timer.Try():
                            # await self.timer_storage.Invoke()

                        await asyncio.sleep(0)

                case _:
                    raise

        finally:
            await self.Terminate()

    def Stop(self):
        if self._enable is False:
            return

        self._enable = False
        self.on_stop.Invoke(self)

    @property
    def enable(self) -> bool:
        return self._enable

    @property
    def window_manager(self) -> 'Managers.WindowManager':
        return Validator.NotNone(self._window_manager)

    @window_manager.setter
    def window_manager(self, manager: 'Managers.WindowManager'):
        self._window_manager = manager

    @property
    def asset_manager(self):
        return Validator.NotNone(self._asset_manager)

    @asset_manager.setter
    def asset_manager(self, manager: 'Managers.AssetManager'):
        self._asset_manager = manager

    @property
    def mesh_manager(self) -> 'Managers.MeshManager':
        return Validator.NotNone(self._mesh_manager)

    @mesh_manager.setter
    def mesh_manager(self, manager: 'Managers.MeshManager'):
        self._mesh_manager = manager

    @property
    def scheduler(self) -> 'TimeoutScheduler':
        return Validator.NotNone(self._scheduler)

    @scheduler.setter
    def scheduler(self, value: 'TimeoutScheduler'):
        self._scheduler = value

    @property
    def timer_storage(self) -> TimerStorage:
        return Validator.NotNone(self._timer_storage)

    @timer_storage.setter
    def timer_storage(self, value: TimerStorage):
        self._timer_storage = value

    def SetExceptionCallaback(self, callback: t.Callable[[Exception], t.Any]):
        self._exception_callback = callback

    def InvokeException(self, ex: Exception):
        try:
            raise ex

        except Exception as ex:
            if self._exception_callback is not None:
                self._exception_callback(ex)
            else:
                raise

    @property
    def on_initialize(self) -> AsyncEvent[Abc.Core]:
        return self._on_initialize

    @property
    def on_initialized(self) -> AsyncEvent[Abc.Core]:
        return self._on_initialized

    @property
    def on_terminate(self) -> AsyncEvent[Abc.Core]:
        return self._on_terminate

    @property
    def on_terminated(self) -> AsyncEvent[Abc.Core]:
        return self._on_terminated

    @property
    def on_stop(self) -> AsyncEvent[Abc.Core]:
        return self._on_stop

    @property
    def on_stoped(self) -> AsyncEvent[Abc.Core]:
        return self._on_stoped

    @property
    def on_simulate(self) -> AsyncEvent[Abc.Core]:
        '''
        Событие симуляции.

        Ожидается.
        '''
        return self._on_simulate

    @property
    def on_draw(self) -> AsyncEvent[Abc.Core]:
        '''
        Событие отрисовки.

        Срабатывает сразу после window_manager.Simulater().

        Ожидается.
        '''
        return self._on_draw

    @property
    def fps_timer(self) -> VariableTimer:
        return Validator.NotNone(self._fps_timer)

    @property
    def sps_timer(self) -> FixedTimer:
        return Validator.NotNone(self._sps_timer)

    @property
    def tps_timer(self) -> VariableTimer:
        return Validator.NotNone(self._tps_timer)


Core: t.Final[Abc.Core] = CoreCls()
