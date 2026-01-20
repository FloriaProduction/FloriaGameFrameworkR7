import typing as t

from FloriaGF import Abc, AsyncEvent, Managers
from FloriaGF.Graphic.Batching import Batch


on_setup = AsyncEvent[Managers.BatchObjectManager]()
on_clear = AsyncEvent[Managers.BatchObjectManager]()

on_setup_batch = AsyncEvent[Abc.Batch]()
on_clear_batch = AsyncEvent[Abc.Batch]()


from . import Window


def Get(name: str) -> Abc.Batch:
    return Window.Get().camera.batch_manager.sequence.GetByName(name)


def GetOrDefault[TDefault: t.Optional[t.Any]](
    name: str,
    default: TDefault = None,
) -> Abc.Batch | TDefault:
    return Window.Get().camera.batch_manager.sequence.GetByNameOrDefault(name, default)


def Create(window: Abc.Window) -> t.Iterable[Abc.Batch]:
    return (Batch(window, index=0, name='entities'),)


def Setup(
    batches: t.Iterable[Abc.Batch],
    batch_manager: t.Optional[Managers.BatchObjectManager] = None,
):
    if batch_manager is None:
        batch_manager = Window.Get().camera.batch_manager

    for batch in batches:
        batch_manager.Register(batch)
        on_setup_batch.Invoke(batch)

    on_setup.Invoke(batch_manager)


def Clear(batch_manager: t.Optional[Managers.BatchObjectManager] = None):
    if batch_manager is None:
        batch_manager = Window.Get().camera.batch_manager

    for batch in batch_manager.sequence:
        on_clear_batch.Invoke(batch)
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
