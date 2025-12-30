from abc import ABC, abstractmethod
import typing as t
from contextlib import contextmanager

from ... import Mixins
from ....AsyncEvent import AsyncEvent

if t.TYPE_CHECKING:
    from uuid import UUID
    from glfw import _GLFWwindow  # pyright: ignore[reportPrivateUsage]

    from ....Managers.ShaderManager import ShaderManager
    from ....Managers.InputManager import InputManager
    from ....Managers.MaterialManager import MaterialManager
    from ..Camera import Camera
    from .... import GL, Types


class Window(
    Mixins.Repr,
    Mixins.ID['UUID'],
    Mixins.Nameable[t.Optional[str]],
    Mixins.Simulatable,
    Mixins.Disposable,
    ABC,
):
    # methods

    @abstractmethod
    def Close(self) -> t.Self: ...

    @abstractmethod
    def GetGLFWWindow(self) -> t.Optional['_GLFWwindow']: ...

    @contextmanager
    @abstractmethod
    def Bind(self):
        yield self

    # properties

    @property
    @abstractmethod
    def should_close(self) -> bool: ...

    @property
    @abstractmethod
    def shader_manager(self) -> 'ShaderManager': ...

    @property
    @abstractmethod
    def material_manager(self) -> 'MaterialManager': ...

    @property
    @abstractmethod
    def input_manager(self) -> 'InputManager': ...

    # events

    @property
    @abstractmethod
    def on_simulate(self) -> AsyncEvent['Window']: ...

    @property
    @abstractmethod
    def on_simulated(self) -> AsyncEvent['Window']: ...

    @property
    @abstractmethod
    def on_close(self) -> AsyncEvent['Window']: ...

    @property
    @abstractmethod
    def on_closed(self) -> AsyncEvent['Window']: ...

    @property
    @abstractmethod
    def on_resize(self) -> AsyncEvent['Window', 'Types.Vec2[int]']: ...

    # window chips

    @abstractmethod
    def GetVSync(self) -> 'GL.hints.vsync': ...
    @abstractmethod
    def SetVSync(self, value: 'GL.hints.vsync'): ...

    @abstractmethod
    def GetCamera(self) -> 'Camera': ...
    @abstractmethod
    def SetCamera(self, value: 'Camera'): ...

    @abstractmethod
    def GetSize(self) -> 'Types.Vec2[int]': ...
    @abstractmethod
    def SetSize(self, x: int, y: int): ...

    @abstractmethod
    def GetWidth(self) -> int: ...
    @abstractmethod
    def SetWidth(self, value: int): ...

    @abstractmethod
    def GetHeight(self) -> int: ...
    @abstractmethod
    def SetHeight(self, value: int): ...

    @abstractmethod
    def GetTitle(self) -> str: ...
    @abstractmethod
    def SetTitle(self, value: str): ...

    @abstractmethod
    def GetVisible(self) -> bool: ...
    @abstractmethod
    def SetVisible(self, value: bool): ...

    @abstractmethod
    def GetResizable(self) -> bool: ...
    @abstractmethod
    def SetResizable(self, value: bool): ...

    @abstractmethod
    def GetDecorated(self) -> bool: ...
    @abstractmethod
    def SetDecorated(self, value: bool): ...

    @abstractmethod
    def GetFloating(self) -> bool: ...
    @abstractmethod
    def SetFloating(self, value: bool): ...

    @abstractmethod
    def SetBackgroundColor(self, value: 'Types.hints.rgb'): ...
    @abstractmethod
    def GetBackgroundColor(self) -> 'Types.RGB[int]': ...

    @property
    @abstractmethod
    def context_version(self) -> 'Types.hints.context_version': ...

    @property
    @abstractmethod
    def double_buffer(self) -> bool: ...

    @property
    def glfw_window(self) -> '_GLFWwindow':
        if (window := self.GetGLFWWindow()) is None:
            raise RuntimeError()
        return window

    @property
    def floating(self) -> bool:
        return self.GetFloating()

    @floating.setter
    def floating(self, value: bool):
        self.SetFloating(value)

    @property
    def decorated(self) -> bool:
        return self.GetDecorated()

    @decorated.setter
    def decorated(self, value: bool):
        self.SetDecorated(value)

    @property
    def size(self) -> tuple[int, int]:
        return self.GetSize()

    @size.setter
    def size(self, value: tuple[int, int]):
        self.SetSize(*value)

    @property
    def width(self) -> int:
        return self.GetWidth()

    @width.setter
    def width(self, value: int):
        self.SetWidth(value)

    @property
    def height(self) -> int:
        return self.GetHeight()

    @height.setter
    def height(self, value: int):
        self.SetHeight(value)

    @property
    def title(self) -> str:
        return self.GetTitle()

    @title.setter
    def title(self, value: str):
        self.SetTitle(value)

    @property
    def visible(self) -> bool:
        return self.GetVisible()

    @visible.setter
    def visible(self, value: bool):
        self.SetVisible(value)

    @property
    def resizable(self) -> bool:
        return self.GetResizable()

    @resizable.setter
    def resizable(self, value: bool):
        self.SetResizable(value)

    @property
    def background_color(self) -> 'Types.RGB[int]':
        return self.GetBackgroundColor()

    @background_color.setter
    def background_color(self, value: 'tuple[int, int, int] | Types.RGB[int]'):
        self.SetBackgroundColor(value)

    @property
    def camera(self) -> 'Camera':
        return self.GetCamera()

    @camera.setter
    def camera(self, value: 'Camera'):
        self.SetCamera(value)

    @property
    def vsync(self) -> t.Literal['full', 'half', 'off']:
        return self.GetVSync()
