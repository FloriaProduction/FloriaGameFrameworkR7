import typing as t


class Avg:
    """Accumulator for incremental average calculation.

    Efficiently computes arithmetic mean without storing all values.
    Suitable for real-time metrics tracking.

    For example::

        avg = Avg()

        avg.Add(60)
        avg.Add(30)

        avg.value  # 45
    """

    __slots__ = ('_sum', '_count')

    def __init__(self) -> None:
        """Initialize Avg instance"""
        super().__init__()

        self._sum: float = 0
        self._count: int = 0

    def Add(self, value: float):
        """Add new value to the accumulator.

        Args:
            value: Numeric value to include in average calculation
        """
        self._sum += value
        self._count += 1

    def Extend(self, values: t.Iterable[float]):
        """Add multiple values efficiently.

        Args:
            values: Iterable of numeric values
        """
        for value in values:
            self.Add(value)

    def Clear(self):
        """Reset accumulator state."""
        self._sum = self._count = 0

    @property
    def count(self) -> int:
        """Current number of accumulated values."""
        return self._count

    @property
    def total(self) -> float:
        """Current accumulated sum of values."""
        return self._sum

    @property
    def value(self) -> float:
        """Current arithmetic mean.

        Returns 0.0 when no values accumulated to avoid division errors.
        """
        return self._sum / self._count if self._count > 0 else 0

    def __len__(self) -> int:
        return self._count

    def __iadd__(self, value: float) -> 'Avg':
        self.Add(value)
        return self
