from abc import ABC
import typing as t


class Repr(ABC):
    __slots__ = ()

    def _GetStrName(self) -> str:
        return f'{self.__class__.__name__}<{id(self)}>'

    def _GetStrKwargs(self) -> dict[str, t.Any]:
        return {}

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        str_kwargs = self._GetStrKwargs()
        return self._GetStrName() + (
            f'({','.join([
                    f'{key}:{value}'
                    for key, value in str_kwargs.items()
                ])})'
            if len(str_kwargs) > 0
            else ''
        )
