from typing import Any, Protocol, ParamSpec, Union


P = ParamSpec('P')


class SyncCallable(Protocol[P]):
    def __call__(self, *args: P.args, **kwds: P.kwargs) -> Any: ...


class AsyncCallable(Protocol[P]):
    async def __call__(self, *args: P.args, **kwds: P.kwargs) -> Any: ...


AnyCallable = Union[SyncCallable[...], AsyncCallable[...]]


class SimpleCallable(SyncCallable[...], Protocol):
    def __call__(self) -> Any: ...


class AsyncSimpleCallable(AsyncCallable[...], Protocol):
    async def __call__(self) -> Any: ...
