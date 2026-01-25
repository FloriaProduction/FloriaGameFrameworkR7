import typing as t

from .. import Abc, Utils, GL
from .Manager import Manager
from ..Stopwatch import stopwatch
from ..Sequences.BatchSequence import BatchSequence


class BatchObjectManager(
    Manager[Abc.Graphic.Batching.Batch],
):
    def __init__(self, window: Abc.Window, *args: t.Any, **kwargs: t.Any):
        super().__init__()

        self._window = window

    @stopwatch
    def Draw(self, camera: Abc.Camera):
        for batch in self.sequence.Sort(lambda batch: batch.index).ToTuple():
            GL.Clear('depth')
            batch.Render(camera)
            batch.Draw()

    @property
    def sequence(self) -> BatchSequence[Abc.Batch]:
        return BatchSequence(self._storage.values())

    @property
    def window(self):
        return self._window

    def Register[T: Abc.Graphic.Batching.Batch](self, item: T) -> T:
        return t.cast(T, super().Register(item))

    @t.overload
    def Remove[T: Abc.Graphic.Batching.Batch](self, item: T, /) -> T: ...
    @t.overload
    def Remove[T: Abc.Graphic.Batching.Batch, TDefault: t.Any](self, item: T, default: TDefault, /) -> T | TDefault: ...

    def Remove(self, *args: t.Any):
        return super().Remove(*args)
