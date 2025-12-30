class PeriodicTrigger:
    """
    Триггер, срабатывающий периодически после определённого количества вызовов.

    Возвращает True каждый раз, когда внутренний счётчик достигает или превышает заданное значение threshold.

    После срабатывания счётчик сбрасывается.
    """

    def __init__(self, threshold: int):
        """
        Инициализирует триггер с заданным пороговым значением.
        """
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        self._counter: int = 0
        self._threshold = threshold

    def Try(self) -> bool:
        """
        Проверяет, нужно ли активировать триггер.
        """
        if self._counter >= self._threshold:
            self._counter = 0
            return True

        self._counter += 1
        return False

    @property
    def current(self) -> int:
        """Текущее значение внутреннего счётчика."""
        return self._counter

    @property
    def threshold(self) -> int:
        """Пороговое значение для срабатывания."""
        return self._threshold
