# FloriaGF - Примеры использования

Этот каталог содержит практические примеры, демонстрирующие ключевые особенности фреймворка.

## Основная концепция

FloriaGF построен на принципе **модульной архитектуры с Dependency Injection** через систему `Computed`. Каждый компонент игры (окна, ресурсы, системы ECS и т.д.) реализуется как независимый модуль с четким жизненным циклом.

## Структура модуля

Каждый модуль обычно содержит:

1. **Computed-объекты** для управления зависимостями
2. **Функции Load/Unload** для инициализации и очистки
3. **Собственные события** для координации между компонентами

## Ключевые компоненты

### Computed - Управление зависимостями
```python
from FloriaGF import Computed, Abc

# Создаем вычисляемую зависимость
window_cmp = Computed[Abc.Window]()

@window_cmp.GetFunc
def _():
    # Логика создания или получения ресурса
    return window_instance

@window_cmp.ClearFunc
def _(value):
    # Логика освобождения ресурса
    if value is not None:
        value.Close()
```

### Load/Unload - Жизненный цикл
```python
async def Load():
    # Инициализация всех зависимостей модуля
    window_cmp()  # Активируем Computed

async def Unload():
    # Корректное освобождение ресурсов
    window_cmp.Clear()
```

### События модулей
Модули могут определять собственные события для координации, пример для игрового уровня:

```python
from FloriaGF import AsyncEvent

# События уровня
on_loaded = AsyncEvent()
on_unloaded = AsyncEvent()

async def Load():
    # ... инициализация ...
    
    # Уведомляем подписчиков о загрузке уровня
    await on_loaded.InvokeAsync()

async def Unload():
    # ... очистка ...
    
    # Уведомляем подписчиков о выгрузке уровня
    await on_unloaded.InvokeAsync()
```

### События объектов
Объекты фреймворка также предоставляют события для реакции на изменения:

```python
from FloriaGF.Extensions.GraphicExt.Graphic.Batching import Sprite3DObject
from FloriaGF.Extensions.GraphicExt.Graphic.Animation import Animation

...

sprite = Sprite3DObject.New(batch, animation)

@sprite.on_change_frame.Register
def _(obj: Sprite3DObject, anim: Animation, frame: int):
    print(f'Спрайт {obj} изменил кадр: {frame}')

@sprite.on_end_animation.Register  
def _(obj: Sprite3DObject, anim: Animation):
    print(f'Анимация {anim} завершена')
```

---

**Примечание:** Все примеры используют асинхронную модель выполнения. Убедитесь, что понимаете работу `async/await` в Python.

Удачной разработки!
