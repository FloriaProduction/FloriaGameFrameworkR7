import time

from .Avg import Avg
from .Timer import VariableTimer


class PerSecond:
    def __init__(self, name: str = 'ps') -> None:
        self._name = name

        self._last_time = time.perf_counter()
        self._avg = Avg()
        self._timer = VariableTimer(1)

        self._print_timer = VariableTimer(1)

    def Call(self):
        now = time.perf_counter()

        self._avg.Add(now - self._last_time)
        self._last_time = now

    def Print(self):
        if self._print_timer.Try():
            print(f'{self._name}~{1/self.value:.2f}({self.value:.4f})' if self.value > 0 else 0)
            self.Clear()

    def Clear(self):
        self._avg.Clear()

    @property
    def value(self) -> float:
        return self._avg.value
