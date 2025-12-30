import typing as t
from pathlib import Path
import aiofiles
import json

from FloriaGF import Convert, Validator


class LanguageManager:
    @classmethod
    async def New(
        cls,
        pathes: dict[str, Path | str],
        default_language: t.Optional[str] = None,
        default: t.Optional[str] = None,
        preload: bool = True,
    ):
        instance = LanguageManager(
            pathes,
            default_language,
        )

        if preload:
            await instance.LoadAll()

        return instance

    def __init__(
        self,
        pathes: dict[str, Path | str],
        default_language: t.Optional[str] = None,
        default: t.Optional[str] = None,
    ):
        self._current_language: str = next(iter(pathes)) if default_language is None else default_language
        self._pathes: dict[str, Path | str] = pathes
        self._languages: dict[str, dict[str, t.Any]] = {}
        self._default: t.Optional[str] = default

    @staticmethod
    async def Load(name: str, path: Path | str) -> dict[str, t.Any]:
        async with aiofiles.open(
            Convert.ToPath(path),
            mode='r',
            encoding='utf-8',
        ) as file:
            if not isinstance(data := json.loads(await file.read()), dict):
                raise
            return data  # pyright: ignore[reportUnknownVariableType]

    async def LoadAll(self):
        for name, path in self._pathes.items():
            self._languages[name] = await self.Load(name, path)

    @t.overload
    def Get(self, *path: str) -> str: ...

    @t.overload
    def Get[TDefault: t.Any](self, *path: str, default: TDefault) -> str | TDefault: ...

    def Get(self, *path: str, **kwargs: t.Any):
        def _Get(lang: dict[str, t.Any], path: tuple[str, ...]) -> t.Optional[str]:
            if not isinstance(lang, dict) or (value := lang.get(path[0])) is None:
                return None

            if len(path) > 1:
                return _Get(value, path[1:])
            return value

        for lang in (
            (
                self._languages[self._current_language],
                *self._languages.values(),
            )
            if self._current_language in self._languages
            else self._languages.values()
        ):
            if (value := _Get(lang, path)) is not None:
                return value

        if 'default' in kwargs:
            return kwargs['default']
        elif self._default is not None:
            return self._default

        raise KeyError(f"Localization key not found: {' -> '.join(path)}, in languages: {', '.join(self._languages.keys())}")

    def SetCurrentLanguage(self, name: str):
        if name not in self._languages:
            raise
        self._current_language = name
