import typing as t


_classses: dict[str, t.Type[t.Any]] = {}


def GetName(cls: t.Type[t.Any]) -> str:
    return f'{cls.__module__}.{cls.__qualname__}'


def Register[T: t.Type[t.Any]](cls: T, alias: t.Optional[str] = None) -> T:
    name = GetName(cls) if alias is None else alias
    
    if name in _classses:
        raise RuntimeError()
    
    _classses[name] = cls
    
    return cls


@t.overload
def GetByName(name: str, /) -> t.Type[t.Any]: ...
    
@t.overload
def GetByName[TDefault: t.Any](name: str, default: TDefault, /) -> t.Type[t.Any] | TDefault: ...

def GetByName(*args: t.Any):
    key = t.cast(str, args[0])
    if len(args) == 1:
        return _classses[key]
    return _classses.get(key, args[1])
    