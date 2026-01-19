import typing as t

from .AsyncEvent import AsyncEvent


class _BaseComputed[
    T: t.Any,
    TFunGet: t.Callable[..., t.Any],
    TFunSet: t.Callable[..., t.Any],
    TFunClear: t.Callable[..., t.Any],
]:
    def __init__(
        self,
        *,
        cached: bool = True,
        get_func: t.Optional[TFunGet] = None,
        set_func: t.Optional[TFunSet] = None,
        clear_func: t.Optional[TFunClear] = None,
    ):
        """
        Инициализирует вычисляемое свойство.

        Args:
            cached: Если True, значение будет кэшироваться после первого вычисления.
                    Если False, функция-геттер будет вызываться каждый раз.
            get_func: Функция для получения значения. Может быть установлена позже
                      через метод GetFunc().
            set_func: Функция для установки значения. Может быть установлена позже
                      через метод SetFunc().
            set_func: Функция для очистки значения. Может быть установлена позже
                      через метод ClearFunc().
        """

        super().__init__()

        self._value: t.Optional[T] = None

        self._get_func: t.Optional[TFunGet] = get_func
        self._set_func: t.Optional[TFunSet] = set_func
        self._clear_func: t.Optional[TFunClear] = clear_func

        self._cached: bool = cached

        self.on_get = AsyncEvent[t.Self]()
        '''Вызывается в момент вызова функции get_func'''
        self.on_set = AsyncEvent[t.Self]()
        '''Вызывается в момент вызова функции set_func'''
        self.on_clear = AsyncEvent[t.Self]()
        '''Вызывается в момент вызова функции clear_func'''

        self.on_value_set = AsyncEvent[t.Self]()
        '''Вызывается в момент присвоения значения при помощи get_func или set_func'''
        self.on_value_cleared = AsyncEvent[t.Self]()
        '''Вызывается в момент очистки значения при помощи clear_func или set_func'''

    @property
    def get_func(self) -> TFunGet:
        """
        Получает текущую функцию-геттер.

        Returns:
            Текущую функцию-геттер

        Raises:
            RuntimeError: Если функция-геттер не была установлена
        """
        if self._get_func is None:
            raise RuntimeError('Getter function is not set')
        return self._get_func

    @property
    def set_func(self) -> TFunSet:
        """
        Получает текущую функцию-сеттер.

        Returns:
            Текущую функцию-сеттер

        Raises:
            RuntimeError: Если функция-сеттер не была установлена
        """
        if self._set_func is None:
            raise RuntimeError('Setter function is not set')
        return self._set_func

    @property
    def clear_func(self) -> t.Optional[TFunClear]:
        """
        Получает текущую функцию-очистки.

        Returns:
            Текущую функцию-очистки
        """
        return self._clear_func

    def GetFunc(self, get_func: TFunGet):
        """
        Устанавливает функцию-геттер.

        Args:
            get_func: Новая функция для получения значения
        """
        self._get_func = get_func

    def SetFunc(self, set_func: TFunSet):
        """
        Устанавливает функцию-сеттер.

        Args:
            set_func: Новая функция для установки значения
        """
        self._set_func = set_func

    def ClearFunc(self, clear_func: TFunClear):
        """
        Устанавливает функцию-сеттер.

        Args:
            set_func: Новая функция для установки значения
        """
        self._clear_func = clear_func

    def Clear(self, call_clear_func: bool = True):
        """
        Очищает кэшированное значение.

        При следующем обращении к значению функция-геттер будет вызвана снова, даже если кэширование включено.

        Args:
            call_clear_func (bool, optional): Вызывает clear_func если True. По умолчанию True.
        """
        if self._value is None:
            return
        if call_clear_func and (clear_func := self._clear_func) is not None:
            clear_func(self._value)
            self.on_clear.Invoke(self)

        self._value = None
        self.on_value_cleared.Invoke(self)


class Computed[T: t.Any](
    _BaseComputed[
        T,
        t.Callable[[], T],
        t.Callable[[T], t.Any],
        t.Callable[[t.Optional[T]], t.Any],
    ]
):
    """
    Синхронное вычисляемое свойство с поддержкой кэширования.

    Этот класс предоставляет интерфейс для вычисляемых значений с синхронными функциями получения и установки.

    Generic Parameters:
        T: Тип хранимого значения

    Example::

        @ (value_cmp := Computed[float]()).GetFunc
        def _():
            return 101

        value = value_cmp() # 101
    """

    @property
    def value(self) -> T:
        """
        Получить текущее значение.

        Если кэширование включено и значение уже вычислено, возвращается кэшированное значение.
        В противном случае вызывается функция-геттер.

        Returns:
            Текущее значение типа T
        """
        if not self._cached or self._value is None:
            self._value = self.get_func()
            self.on_get.Invoke(self)

        if self._value is not None:
            self.on_value_set.Invoke(self)

        return self._value

    @value.setter
    def value(self, value: T):
        """
        Устанавливает новое значение.

        Args:
            value: Новое значение для установки

        Note:
            Вызывает функцию-сеттер с переданным значением
        """

        self._value = self.set_func(value)
        self.on_set.Invoke(self)

        if self._value is None:
            self.on_value_cleared.Invoke(self)
        else:
            self.on_value_set.Invoke(self)

    def __call__(self, *args: t.Any, **kwds: t.Any) -> T:
        """
        Позволяет использовать экземпляр как вызываемый объект.

        Returns:
            Текущее значение типа T
        """
        return self.value


class ComputedAsync[T: t.Any](
    _BaseComputed[
        T,
        t.Callable[[], t.Coroutine[t.Any, t.Any, T]],
        t.Callable[[T], t.Coroutine[t.Any, t.Any, t.Any]],
        t.Callable[[T], t.Coroutine[t.Any, t.Any, t.Any]],
    ]
):
    """
    Асинхронное вычисляемое свойство с поддержкой кэширования.

    Этот класс предоставляет интерфейс для вычисляемых значений с асинхронными функциями получения и установки.

    Generic Parameters:
        T: Тип хранимого значения

    Example::

        api_data_cmp = ComputedAsync[dict[str, t.Any]]()

        @api_data_cmp.GetFunc
        async def _():
            return {'key': 'value'}


        @api_data_cmp.SetFunc
        async def _(data: dict[str, t.Any]):
            pass

        ...

        await api_data_cmp()  # Асинхонное получение
    """

    async def GetValue(self) -> T:
        """
        Асинхронно получить текущее значение.

        Если кэширование включено и значение уже вычислено, возвращается кэшированное значение.
        В противном случае асинхронно вызывается функция-геттер.

        Returns:
            Текущее значение типа T
        """
        if not self._cached or self._value is None:
            self._value = await self.get_func()
            self.on_get.Invoke(self)

        if self._value is not None:
            self.on_value_set.Invoke(self)

        return self._value

    async def SetValue(self, value: T):
        """
        Асинхронно устанавливает новое значение.

        Args:
            value: Новое значение для установки
        """
        self._value = await self.set_func(value)
        self.on_set.Invoke(self)

        if self._value is None:
            self.on_value_cleared.Invoke(self)
        else:
            self.on_value_set.Invoke(self)

    async def __call__(self, *args: t.Any, **kwds: t.Any) -> T:
        """
        Позволяет использовать экземпляр как асинхронно вызываемый объект.

        Returns:
            Текущее значение типа T
        """
        return await self.GetValue()
