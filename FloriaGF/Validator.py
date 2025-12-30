import typing as t
import types as ts


def Raiser(exc: Exception | str) -> t.Any:
    """Raises exception in expression contexts.

    Enables exception throwing inside ternary operators and lambda expressions where
    direct 'raise' statements are syntactically invalid.

    Args:
        exc: Exception instance to raise
    """
    raise Exception(exc) if isinstance(exc, str) else exc


def NotNone[T: t.Any](
    obj: t.Optional[T],
    *,
    error: t.Optional[Exception | str] = None,
) -> T:
    """Validates object is not None.

    Returns original object if valid. Raises RuntimeError (or custom exception) on failure.

    Args:
        obj: Object to validate
        error: Custom exception or error message. Defaults to generic RuntimeError.

    Returns:
        Validated non-None object

    Raises:
        RuntimeError: If obj is None and no custom error provided
        Exception: Custom exception specified in `error` parameter
    """
    return obj if obj is not None else Raiser('Object is None' if error is None else error)


def Instance[T: t.Any](
    obj: t.Any,
    type: t.Type[T],
    *,
    error: t.Optional[Exception | str] = None,
) -> T:
    """Validates object type.

    Returns original object if isinstance(obj, type). Raises exception on failure.

    Args:
        obj: Object to validate
        type: Expected type
        error: Custom exception or error message. Defaults to generic RuntimeError.

    Returns:
        Validated object of expected type

    Raises:
        RuntimeError: If type check fails and no custom error provided
        Exception: Custom exception specified in `error` parameter
    """
    return obj if isinstance(obj, type) else Raiser(f'Expected {type}, got {type(obj)}' if error is None else error)


def HasNone[T: t.Any](data: t.Iterable[t.Optional[T]]) -> bool:
    return any(item is not None for item in data)


def AllIsNone[T: t.Any](data: t.Iterable[t.Optional[T]]) -> bool:
    return all(item is None for item in data)


def NotEmpty[T: t.Iterable[t.Any]](
    data: T,
    *,
    error: t.Optional[Exception | str] = None,
) -> T:
    for _ in data:
        return data
    return Raiser(f'Iterable is empty' if error is None else error)
