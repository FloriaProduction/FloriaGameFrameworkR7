import typing as t
import types as ts
from contextlib import contextmanager
from time import perf_counter
from collections import deque
import functools

if t.TYPE_CHECKING:
    from . import Protocols


class Stopwatch:
    """Таймер для измерения времени выполнения.

    Example::

        stopwatch = Stopwatch(5)

        with stopwatch:
            ...
    """

    __slots__ = (
        '_start_time',
        '_last_value',
        '_samples',
    )

    def __init__(self, max_samples: int = 10):
        """Инициализация Stopwatch.

        Args:
            max_samples (int, optional): Максимальное количество хранимых замеров. По умолчанию 10.
        """
        self._start_time: t.Optional[float] = None

        self._last_value: t.Optional[float] = None
        self._samples: deque[float] = deque(maxlen=max_samples)

    def __enter__(self, *args: t.Any, **kwargs: t.Any):
        """Запуск таймера при входе в контекст."""
        self.Start()
        return self

    def __exit__(self, *args: t.Any, **kwargs: t.Any):
        """Остановка таймера при выходе из контекста."""
        self.Stop()

    @contextmanager
    def Bind(self):
        """Альтернативный способ измерения через контекстный менеджер."""
        try:
            self.Start()

            yield self

        finally:
            self.Stop()

    def Start(self):
        """Запуск таймера.

        Raises:
            RuntimeError: Если таймер уже запущен.
        """
        if self._start_time is not None:
            raise RuntimeError('Stopwatch is already running')
        self._start_time = perf_counter()

    def Stop(self) -> float:
        """
        Остановка таймера и сохранение результата.

        Returns:
            float: Прошедшее время в секундах.

        Raises:
            RuntimeError: Если таймер не запущен.
        """
        if self._start_time is None:
            raise RuntimeError("Stopwatch is not running")

        self._last_value = perf_counter() - self._start_time
        self._samples.append(self._last_value)

        self._start_time = None
        return self._last_value

    def Lap(self) -> float:
        """
        Получить промежуточное время без остановки таймера.

        Returns:
            float: Время с начала измерения.

        Raises:
            RuntimeError: Если таймер не запущен.
        """
        if self._start_time is None:
            raise RuntimeError("Stopwatch is not running")

        return perf_counter() - self._start_time

    def Reset(self):
        """Сброс всех замеров и текущего значения."""
        self._samples.clear()
        self._last_value = None

    @property
    def is_running(self) -> bool:
        """Проверка, запущен ли таймер."""
        return self._start_time is not None

    @property
    def last(self) -> float:
        """Последнее зафиксированное время."""
        if self._last_value is None:
            raise
        return self._last_value

    @property
    def min(self) -> float:
        """Минимальное значение из всех сохранённых замеров."""
        return min(*self._samples) if self.count > 0 else 0

    @property
    def max(self) -> float:
        """Максимальное значение из всех сохранённых замеров."""
        return max(*self._samples) if self.count > 0 else 0

    @property
    def avg(self) -> float:
        """Среднее значение всех сохранённых замеров."""
        if (count := len(self._samples)) > 0:
            return sum(self._samples) / count
        return 0

    @property
    def total(self) -> float:
        """Сумма всех сохранённых замеров."""
        return sum(self._samples)

    @property
    def count(self) -> int:
        """Количество сохранённых замеров."""
        return len(self._samples)

    def __repr__(self) -> str:
        avg = round(self.avg, 6) if self.count > 0 else None
        last = round(self.last, 6) if self._last_value is not None else None
        return f'Stopwatch<{id(self)}>(avg: {avg}(~{None if avg is None else round(1 / avg, 1)}), last: {last}(~{None if last is None else round(1 / last, 1)}))'

    def __str__(self) -> str:
        return self.__repr__()

    
    
def stopwatch[
    TFunc: Protocols.Functions.SyncCallable[...],
](
    func: TFunc,
    stopwatch: t.Optional[Stopwatch] = None,
) -> TFunc:
    """Декоратор для измерения времени выполнения функций и методов."""
    
    stopwatch = Stopwatch() if stopwatch is None else stopwatch
    
    @functools.wraps(func)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        with stopwatch:
            return func(*args, **kwargs)
    
    wrapper.__stopwatch__ = stopwatch # pyright: ignore[reportAttributeAccessIssue]
    
    return t.cast(TFunc, wrapper)
