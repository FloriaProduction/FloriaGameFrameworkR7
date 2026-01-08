from contextlib import contextmanager


class Flag:
    """
    Управляемый флаг с поддержкой контекстного менеджера.

    Предоставляет механизм временного установления флага с
    автоматическим сбросом при выходе из контекста.

    Example::

        flag = Flag()

        ...

        with flag.Bind():
            # Флаг установлен в True
            ...

        # Флаг автоматически сброшен в False

        ...

        if flag:
            raise Exception(...)
    """

    def __init__(self, value: bool = False):
        """
        Инициализирует флаг начальным значением
        """
        self._value: bool = value

    def __bool__(self) -> bool:
        """Возвращает текущее состояние флага для использования в условиях"""
        return self._value

    @contextmanager
    def Bind(self):
        """
        Контекстный менеджер для временного установления флага.

        Устанавливает флаг в True при входе в контекст и гарантированно сбрасывает в False при выходе

        Example::

            with flag.Bind():
                # Флаг установлен в True
                ...
            # Флаг автоматически сброшен в False
        """
        try:
            self._value = True
            yield

        finally:
            self._value = False

    def Set(self):
        """Устанавливает флаг в состояние True"""
        self._value = True

    def Reset(self):
        """Сбрасывает флаг в состояние False"""
        self._value = False

    def Toggle(self):
        """Инвертирует текущее состояние флага"""
        self._value = not self._value

    @property
    def value(self) -> bool:
        """Текущее состояние флага"""
        return self._value
