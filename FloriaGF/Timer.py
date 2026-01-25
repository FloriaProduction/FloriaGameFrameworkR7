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
