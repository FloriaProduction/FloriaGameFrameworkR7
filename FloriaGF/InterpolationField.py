import typing as t

from .Core import Core

if t.TYPE_CHECKING:
    from .AsyncEvent import AsyncEvent


class InterpolationState:
    """Состояние интерполяции для отслеживания асинхронного обновления."""

    __slots__ = (
        '_timer_tick',
        '_event',
        '_event_id',
        '_callback_func',
        '_check_func',
        '__weakref__',
    )

    def __init__(
        self,
        callback_func: t.Callable[[], t.Any],
        check_func: t.Callable[[], bool],
        event: 'AsyncEvent[...]',
    ):
        """Инициализирует состояние интерполяции.

        Args:
            callback_func (t.Callable[[], t.Any]): Функция, вызываемая при обновлении.
            check_func (t.Callable[[], bool]): Функция проверки необходимости продолжения интерполяции.
            event (AsyncEvent[...]): Асинхронное событие для планирования обновлений.
        """

        self._timer_tick: t.Optional[int] = None

        self._event: 'AsyncEvent[...]' = event
        self._event_id: t.Optional[int] = None

        self._callback_func: t.Callable[[], t.Any] = callback_func
        self._check_func: t.Callable[[], bool] = check_func

    def RegisterEvent(self):
        """Регистрирует обработчик в асинхронном событии."""

        if self._event_id is not None:
            return

        self._event_id = self._event.Register(self._Update)

    def RemoveEvent(self):
        """Удаляет обработчик из асинхронного события."""

        if self._event_id is None:
            return

        self._event.Remove(self._event_id)
        self._event_id = None

    def _Update(self, *args: t.Any, **kwargs: t.Any):
        if not self._check_func():
            self.RemoveEvent()
            return

        self._callback_func()


class InterpolationField[T: t.Any]:
    """
    Универсальное поле с поддержкой интерполяции между значениями.

    Предназначено для плавного изменения значений между тиками обновления игры.
    Поддерживает любые типы данных с пользовательской функцией интерполяции.
    """

    __slots__ = (
        '_timer_tick',
        '_event',
        '_event_id',
        '_next_value',
        '_prev_value',
        '_interpolation_func',
        '_callback_func',
        '_check_func',
        '__weakref__',
    )

    def __init__(
        self,
        value: T,
        interpolation_func: t.Callable[[T, T, float], T],
        callback_func: t.Callable[[T], t.Any],
        event: 'AsyncEvent[...]',
        check_func: t.Callable[[t.Optional[T], T], bool] = lambda prev, next: prev is not None and prev != next,
    ):
        """Инициализирует поле интерполяции.

        Args:
            value (T): Начальное значение.
            interpolation_func (t.Callable[[T, T, float], T]): Функция интерполяции (prev, next, progress) -> value.
            callback_func (t.Callable[[T], t.Any]): Callback, вызываемый при изменении значения.
            event (AsyncEvent[...]): Асинхронное событие для обновлений.
            check_func (t.Callable[[t.Optional[T], T], bool], optional): Функция проверки необходимости интерполяции между значениями. Defaults to lambdaprev.
        """

        self._timer_tick: t.Optional[int] = None

        self._event: AsyncEvent[...] = event
        self._event_id: t.Optional[int] = None

        self._next_value: T = value
        self._prev_value: t.Optional[T] = None

        self._interpolation_func: t.Callable[[T, T, float], T] = interpolation_func
        self._callback_func: t.Callable[[T], t.Any] = callback_func
        self._check_func: t.Callable[[t.Optional[T], T], bool] = check_func

    def _Update(self, *args: t.Any, **kwargs: t.Any):
        if not self._check_func(self._prev_value, self._next_value):
            self.RemoveEvent()
            return

        self._callback_func(self.GetValue())

    def RegisterEvent(self):
        """Регистрирует обработчик в асинхронном событии."""

        if self._event_id is not None:
            return

        self._event_id = self._event.Register(self._Update)

    def RemoveEvent(self):
        """Удаляет обработчик из асинхронного события."""

        if self._event_id is None:
            return

        self._event.Remove(self._event_id)
        self._event_id = None

    def GetValue(self) -> T:
        """Получает текущее интерполированное значение.

        Если интерполяция не требуется или завершена, возвращает целевое значение.
        Иначе вычисляет интерполированное значение на основе прогресса.

        Returns:
            Текущее значение (интерполированное или целевое)
        """

        if (
            self._prev_value is None
            or (timer_tick := self._timer_tick) is None
            or (progress := Core.sps_timer.GetProgressByTick(timer_tick)) >= 1
        ):
            self._prev_value = None
            return self._next_value

        return self._interpolation_func(
            self._prev_value,
            self._next_value,
            progress,
        )

    def SetValue(
        self,
        value: T,
        flash: bool = True,
    ):
        """Устанавливает новое значение поля.

        Args:
            value (T): Новое целевое значение.
            flash (bool, optional): \n
                Если True, значение устанавливается мгновенно без интерполяции. \n
                Если False, начинается плавная интерполяция от предыдущего значения. \n
                Defaults to True.
        """
        if flash:
            self._prev_value = None

        else:
            self._prev_value = self._next_value
            self._timer_tick = Core.sps_timer.tick
            self.RegisterEvent()

        self._next_value = value
