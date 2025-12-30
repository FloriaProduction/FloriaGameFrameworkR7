import typing as t
import pathlib

from .. import Abc, Assets, Utils
from .Manager import Manager
from ..Sequences import AssetSequence
from ..Loggers import asset_manager_logger
from ..AsyncEvent import AsyncEvent

if t.TYPE_CHECKING:
    from ..Assets import Asset


class AssetManager(
    Manager['Asset'],
):
    @property
    def on_load(self) -> AsyncEvent['AssetManager', pathlib.Path]:
        return self._on_load

    @property
    def on_loaded(self) -> AsyncEvent['AssetManager', pathlib.Path, 'Asset']:
        return self._on_loaded

    def __init__(
        self,
        asset_types: t.Optional[
            dict[
                tuple[str, ...],
                t.Type['Asset'],
            ]
        ] = None,
    ):
        super().__init__()

        self.asset_types: dict[tuple[str, ...], t.Type['Asset']] = {
            ('.png', '.jpg', '.jpeg'): Assets.Image,
            ('.txt', '.log'): Assets.Text,
            ('.json',): Assets.Json,
        }
        if asset_types is not None:
            self.asset_types.update(asset_types)

        self._on_load = AsyncEvent['AssetManager', pathlib.Path]()
        self._on_loaded = AsyncEvent['AssetManager', pathlib.Path, 'Asset']()

    def GetAssetTypeByExtension(
        self,
        suffix: str,
        default: t.Type['Asset'] = Assets.Asset,
    ) -> t.Type['Asset']:
        for key, type in self.asset_types.items():
            if suffix in key:
                return type
        return default

    @t.overload
    async def LoadFile(self, path: str | pathlib.Path, /) -> 'Asset': ...
    @t.overload
    async def LoadFile[T: 'Asset'](self, path: str | pathlib.Path, type: t.Type[T]) -> T: ...

    async def LoadFile(self, path: str | pathlib.Path, type: t.Optional[t.Type['Asset']] = None):
        if isinstance(path, str):
            path = pathlib.Path(path)

        self.on_load.Invoke(self, path)

        asset_cache = self.sequence.WithPath(path).FirstOrDefault()
        if asset_cache is not None and (type is None or isinstance(asset_cache, type)):
            asset = asset_cache

        else:
            if not path.exists():
                raise ValueError()

            if type is None:
                type = self.GetAssetTypeByExtension(path.suffix)

            asset = self.Register(await type.Load(path))

            asset_manager_logger.info(f'LoadFile "{path}"\ttype=\'{type.__module__}.{type.__qualname__}\'')

            self.on_loaded.Invoke(self, path, asset)

        return asset

    async def LoadDir(self, dir: str | pathlib.Path, depth_or_pattern: bool | str = False):
        asset_manager_logger.info(
            f'''LoadDir "{dir}" {
            f'depth={depth_or_pattern}' 
            if isinstance(depth_or_pattern, bool) else 
            f'pattern={depth_or_pattern}'
        }...'''
        )

        if isinstance(dir, str):
            dir = pathlib.Path(dir)

        if not dir.is_dir():
            raise ValueError()

        if depth_or_pattern is True:
            matches = dir.rglob("*")
        elif depth_or_pattern is False:
            matches = dir.glob("*")
        else:
            matches = dir.glob(depth_or_pattern)

        await Utils.WaitCors(self.LoadFile(path) for path in matches if path.is_file())

    async def Load(self, path_or_dir: str | pathlib.Path):
        asset_manager_logger.info(f'Load "{path_or_dir}"...')

        if isinstance(path_or_dir, str):
            path_or_dir = pathlib.Path(path_or_dir)

        if path_or_dir.is_file():
            await self.LoadFile(path_or_dir)

        elif path_or_dir.is_dir():
            await self.LoadDir(path_or_dir)

        else:
            raise ValueError()

    @property
    def sequence(self) -> AssetSequence[Asset]:
        return AssetSequence(self._storage.values())

    async def Clear(self):
        asset_manager_logger.info(f'Clear {self.count} assets')

        for asset in (*self.sequence,):
            self.Remove(asset)

    def Register[T: Asset](self, item: T) -> T:
        return t.cast(T, super().Register(item))

    @t.overload
    def Remove[T: 'Asset'](self, item: T, /) -> T: ...
    @t.overload
    def Remove[T: 'Asset', TDefault: t.Any](self, item: T, default: TDefault, /) -> T | TDefault: ...

    def Remove(self, *args: t.Any):
        return super().Remove(*args)
