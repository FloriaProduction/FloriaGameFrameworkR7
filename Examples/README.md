# FloriaGameFramework - Примеры использования

Этот каталог содержит практические примеры, демонстрирующие модульную архитектуру FloriaGameFramework.

## Философия архитектуры

FloriaGameFramework построен на принципе **модульной архитектуры с инверсией зависимостей**. Каждый компонент игры реализуется как независимый модуль с четким жизненным циклом, что обеспечивает:

1. **Разделение ответственности** - каждый модуль решает одну задачу
2. **Легкую заменяемость** - модули можно менять без изменения системы
3. **Предсказуемость** - четкий порядок инициализации и очистки
4. **Масштабируемость** - простую интеграцию новых компонентов

## Ключевые концепции

### Модули жизненного цикла
Модули с методами `Load()`/`Unload()` управляют собственными ресурсами:

```python
async def Load():
    """Инициализация всех зависимостей модуля"""
    ...

async def Unload():
    """Корректное освобождение ресурсов"""
    ...
```

### Событийные подписчики
Модули могут подписываться на события других модулей через систему событий:

```python
# Импорт модуля окна
from . import Window

# Подписка на событие модуля
@Window.on_setup
def _(window: Abc.Window):
    # Реакция на инициализацию окна
    ...
```

### Ядро и расширения
- **FloriaGF** - базовые системы, менеджеры, абстракции
- **FloriaGF.Extensions** - расширения: графика, ECS, языки и другое

## Шаблоны для разработки

### 1. Базовый модуль
```python
# Module.py
from FloriaGF import AsyncEvent

on_load = AsyncEvent[...]()
on_unload = AsyncEvent[...]()

async def Load():
    # Загрузка
    await on_load.InvokeAsync()

async def Unload():
    # Выгрузка
    await on_unload.InvokeAsync()
```

### 2. Модуль-подписчик
```python
# SubscriberModule.py
from . import Module

# Реакции на события другого модуля

@Module.on_load
def _():
    print("Module загружен!")

@Module.on_unload
def _():
    print("Module выгружен!")
```

### 3. Модуль окна
```python
# Window.py
import typing as t

from FloriaGF import Core, Abc, Validator, AsyncEvent
from FloriaGF.Graphic import Window, Camera

on_setup = AsyncEvent[Abc.Window]()
on_clear = AsyncEvent[Abc.Window]()

on_load = AsyncEvent[Abc.Window]()
on_unload = AsyncEvent[Abc.Window]()

_window: t.Optional[Abc.Window] = None

def Get():
    return Validator.NotNone(_window, error='Window is not initialized')

def Setup():
    window = Window((1280, 720))
    Core.window_manager.Register(window)
    on_setup.Invoke(window)
    return window

def Clear(window: Abc.Window):
    window.Close()
    on_clear.Invoke(window)

async def Load():
    global _window

    if _window is not None:
        raise Exception('Module already loaded')

    _window = Setup()
    await on_load.InvokeAsync(_window)

async def Unload():
    global _window

    if _window is None:
        return

    Clear(_window)
    await on_unload.InvokeAsync(_window)

    _window = None
```
[Расширенная версия](https://github.com/FloriaProduction/FloriaGameFrameworkR7/blob/main/Examples/Window.py)

### 4. Модуль батчинга
```python
# Batching.py
import typing as t

from FloriaGF import Abc, AsyncEvent
from FloriaGF.Graphic import Batch
from FloriaGF.Managers import BatchObjectManager

on_setup = AsyncEvent[BatchObjectManager]()
on_clear = AsyncEvent[BatchObjectManager]()

from . import Window

def Get(name: str) -> Abc.Batch:
    return Window.Get().camera.batch_manager.sequence.GetByName(name)

def Create(window: Abc.Window) -> t.Iterable[Abc.Batch]:
    return (Batch(window, index=0, name='entities'),)

def Setup(
    batches: t.Iterable[Abc.Batch],
    batch_manager: t.Optional[BatchObjectManager] = None,
):
    if batch_manager is None: 
        batch_manager = Window.Get().camera.batch_manager
    batch_manager.RegisterMany(*batches)

    on_setup.Invoke(batch_manager)

def Clear(batch_manager: t.Optional[BatchObjectManager] = None):
    if batch_manager is None:
        batch_manager = Window.Get().camera.batch_manager
    batch_manager.RemoveAll()

    on_clear.Invoke(batch_manager)

@Window.on_setup
def _(window: Abc.Window):
    Setup(Create(window), window.camera.batch_manager)

    @window.on_camera_change
    def _(window: Abc.Window, new: Abc.Camera, prev: Abc.Camera):
        Clear(prev.batch_manager)
        Setup(Create(window), new.batch_manager)

@Window.on_clear
def _(window: Abc.Window):
    Clear(window.camera.batch_manager)
```
[Расширенная версия](https://github.com/FloriaProduction/FloriaGameFrameworkR7/blob/main/Examples/Batching.py)

### 5. Модуль ввода
```python
# Input.py
from FloriaGF import Managers, AsyncEvent, Abc

on_setup = AsyncEvent[Managers.Input.InputManager]()
on_clear = AsyncEvent[Managers.Input.InputManager]()

from . import Window

def Setup(input_manager: Managers.Input.InputManager):
    on_setup.Invoke(input_manager)

def Clear(input_manager: Managers.Input.InputManager):
    on_clear.Invoke(input_manager)

@Window.on_setup
def _(window: Abc.Window):
    Setup(window.input_manager)

@Window.on_clear
def _(window: Abc.Window):
    Clear(window.input_manager)
```
[Расширенная версия](https://github.com/FloriaProduction/FloriaGameFrameworkR7/blob/main/Examples/Input.py)

### 5.1. Подписчик к модулю ввода
```python
#InputMaps.py
import typing as t

from FloriaGF.Managers.Input import InputManager, Actions

from . import Input

@Input.on_setup
async def _(im: InputManager):
    im.SetMaps({
        'core': {
            'exit': {
                'type': 'press',
                'key': 'f10',
                'stages': 'press',
            },
        },
    })

    @Actions.PressHandler(im, 'core', 'exit').event
    def _(*args: t.Any):
        from FloriaGF import Core

        Core.Stop()
```
[Расширенная версия](https://github.com/FloriaProduction/FloriaGameFrameworkR7/blob/main/Examples/InputMaps.py)

## Структура приложения

```python
# main.py
from FloriaGF import Core
from FloriaGF.Managers import ModuleManager

import Game

@Core.on_initialized
async def _(_):
    await ModuleManager.Load(
        Game.Resources,
        Game.Window,
    )

@Core.on_terminate
async def _(_):
    await ModuleManager.Unload(
        Game.Window,
        Game.Resources,
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(Core.Run())
```

## Советы по разработке

1. **Один модуль - одна ответственность**
2. **Используйте события для слабой связи**
3. **Соблюдайте порядок загрузки/выгрузки**
4. **Документируйте зависимости модуля**

---

**Примечание:** Фреймворк часто работает асинхронно. Убедитесь, что понимаете работу `async/await` в Python. Для отладки используйте события жизненного цикла.

**Удачной разработки с FloriaGameFramework!**