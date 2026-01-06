import typing as t


_classses: dict[str, t.Type[t.Any]] = {}


def GetName(cls: t.Type[t.Any]) -> str:
    return f'{cls.__module__}.{cls.__qualname__}'


def Register[T: t.Type[t.Any]](cls: T, alias: t.Optional[str] = None) -> T:
    if (name := GetName(cls) if alias is None else alias) in _classses:
        raise RuntimeError()

    _classses[name] = cls

    return cls


def GetByName(name: str) -> t.Type[t.Any]:
    return _classses[name]


def GetByNameOrDefault[TDefault: t.Optional[t.Any]](name: str, default: TDefault = None) -> t.Type[t.Any] | TDefault:
    return _classses.get(name, default)  # pyright: ignore[reportReturnType]
