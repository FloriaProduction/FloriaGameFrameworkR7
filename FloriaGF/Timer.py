import typing as t
from time import perf_counter


class VariableTimer:
    """Repeating timer with configurable interval

    Triggers at fixed intervals but does not accumulate missed ticks
    Ideal for non-critical periodic tasks like UI updates

    For example::

        timer = VariableTimer(1/120)
        while running:
            if timer.Try():
                ...

    """

    __slots__ = (
        '_interval',
        '_next_time',
        '_last_time',
    )

    def __init__(self, interval: float = 0):
        """Initialize VariableTimer instance

        Args:
            interval (float, optional): Time between triggers in seconds (must be >= 0). Defaults to 0.

        Raises:
            ValueError: If interval is negative
        """
        if interval < 0:
            raise ValueError("Interval must be greate or equal 0")
        self._interval: float = interval
        self._next_time: float = perf_counter() + self.interval
        self._last_time: float = 0

    def Try(self):
        """Attempt triggering based on elapsed time

        Updates trigger timestamp when activated

        Returns:
            True if timer triggered, False otherwise
        """
        result = False
        now = perf_counter()

        if now >= self._next_time:
            self._next_time = now + self.interval
            result = True

        self._last_time = now
        return result

    @property
    def interval(self) -> float:
        """Current interval duration in seconds"""
        return self._interval

    @property
    def last_time(self) -> float:
        return self._last_time

    @property
    def progress(self) -> float:
        return max(0, min(1, perf_counter() - self.last_time) / self.interval)


class FixedTimer:
    """Fixed-interval timer

    Tracks ideal tick progression based on elapsed time and triggers discrete ticks when the ideal count exceeds processed ticks

    For example::

        timer = FixedTimer(1/20)
        while running:
            if timer.Try():
                ...
    """

    __slots__ = ('_interval', '_count', '_start_time')

    def __init__(self, interval: float):
        """Initialize FixedTimer instance

        Args:
            interval (float): Time between ticks in seconds (must be > 0)

        Raises:
            ValueError: If interval is not positive
        """
        if interval <= 0:
            raise ValueError("Interval must be positive")
        self._interval: float = interval
        self._count: int = 0
        self._start_time: float = perf_counter()

    def Try(self):
        """Attempt to process next tick

        Advances internal counter if sufficient time has elapsed since last processed tick

        Returns:
            True if tick was processed, False otherwise
        """
        if self.ideal_ticks > self._count:
            self._count += 1
            return True
        return False

    @property
    def interval(self):
        """Fixed duration between ticks (seconds)"""
        return self._interval

    @property
    def tick(self) -> int:
        """Number of ticks processed"""
        return self._count

    @property
    def ideal_ticks(self) -> float:
        """Theoretical tick count based on elapsed time

        Represents how many ticks should have occurred since timer start, calculated as: (current_time - start_time) / interval
        """
        return (perf_counter() - self._start_time) / self._interval

    @property
    def progress(self) -> float:
        return self.GetProgressByTick(self.tick)

    def GetProgressByTick(self, tick: t.Optional[int]) -> float:
        return 1 if tick is None else (1 - max(0, min(1, tick - self.ideal_ticks)))

    # class TimerABC[TDelay: t.Any = float](ABC):
    #     @property
    #     @abstractmethod
    #     def delay(self) -> TDelay: ...
    #     @delay.setter
    #     @abstractmethod
    #     def delay(self, value: TDelay): ...

    # class SyncTimerABC[TDelay: t.Any = float](TimerABC[TDelay]):
    #     @abstractmethod
    #     def Try(self, *args: t.Any, **kwargs: t.Any) -> t.Any: ...

    # class AsyncTimerABC[TDelay: t.Any = float](TimerABC[TDelay]):
    # @abstractmethod
    # async def Try(self, *args: t.Any, **kwargs: t.Any) -> t.Any: ...


# class TimerCU(SyncTimerABC):
#     '''
#     catch-up timer
#     '''

#     def __init__(self, delay: float, *callbacks: t.Callable[[], t.Any]):
#         if delay <= 0:
#             raise ValueError()

#         self._delay: float = delay
#         self._time: float = perf_counter()
#         self._last_count: int = 0

#         self._callbacks: list[t.Callable[[], t.Any]] = list(callbacks)

#     def AddCallbacks(self, *callbacks: t.Callable[[], t.Any]):
#         self._callbacks.extend(callbacks)

#     def Try(self, *callbacks: t.Callable[[], t.Any]):
#         diff = perf_counter() - self._time

#         all_count = round(diff / self.delay)

#         count = all_count - self._last_count
#         all_callbacks = (*callbacks, *self._callbacks)
#         for _ in range(count):
#             for callback in all_callbacks:
#                 callback()

#         self._last_count = all_count

#     @property
#     def delay(self) -> float:
#         return self._delay

#     @delay.setter
#     def delay(self, value: float):
#         self._delay = value


class TimerStorage:
    pass
    # def __init__(self) -> None:
    #     self._timers: dict[int, TimerABC] = {}

    # def Register(self, timer: TimerABC) -> int:
    #     key = hash(timer)
    #     self._timers[key] = timer
    #     return key

    # def Remove(self, key: int):
    #     self._timers.pop(key, None)

    # async def Invoke(self, *args: t.Any, **kwargs: t.Any) -> float:
    #     next_time: float = perf_counter() + 0.001

    #     for timer in tuple(self._timers.values()):
    #         timer.Try()

    #     return next_time
