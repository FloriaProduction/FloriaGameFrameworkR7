import typing as t
import glfw

from uuid import UUID, uuid4
from contextlib import contextmanager

from ... import Abc, Utils, Managers, Convert, GL, Types
from ...Config import Config
from ..Objects.VAO import VAO
from ...AsyncEvent import AsyncEvent
from ..Camera import Camera
from ...Stopwatch import stopwatch


class Window(Abc.Graphic.Windows.Window):
    def __init__(
        self,
        size: Types.hints.size_2d,
        title: str = 'Title',
        name: t.Optional[str] = None,
        *args: t.Any,
        visible: bool = True,
        resizable: bool = True,
        maximized: bool = False,
        decorated: bool = True,
        floating: bool = False,
        vsync: t.Optional[GL.hints.vsync] = None,
        background_color: Types.hints.rgb = (255, 255, 255),
        double_buffer: bool = True,
        **kwargs: t.Any,
    ):
        super().__init__()

        self._id: UUID = uuid4()
        self._name: t.Optional[str] = name

        self._vsync: GL.hints.vsync = Config.VSYNC if vsync is None else vsync
        self._background_color = Types.RGB.New(background_color)
        self._context_version: tuple[int, int] = (4, 2)
        self._double_buffer: bool = double_buffer

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, self.context_version[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, self.context_version[1])
        glfw.window_hint(glfw.VISIBLE, False)
        glfw.window_hint(glfw.DOUBLEBUFFER, GL.Convert.ToOpenGLBool(self.double_buffer))
        glfw.window_hint(glfw.SAMPLES, 4)

        glfw.window_hint(glfw.RESIZABLE, resizable)
        glfw.window_hint(glfw.MAXIMIZED, maximized)
        glfw.window_hint(glfw.DECORATED, decorated)
        glfw.window_hint(glfw.FLOATING, floating)

        self._window: t.Optional[GL.Window.GLFWWindow] = GL.Window.Create(size, title)

        self._on_simulate = AsyncEvent[Abc.Window]()
        self._on_simulated = AsyncEvent[Abc.Window]()
        self._on_close = AsyncEvent[Abc.Window]()
        self._on_closed = AsyncEvent[Abc.Window]()
        self._on_resize = AsyncEvent[Abc.Window, Types.Vec2[int]]()

        self._input_manager: Managers.InputManager = Managers.InputManager(self)
        self._shader_manager: Managers.ShaderManager = Managers.ShaderManager(self)
        self._material_manager: Managers.MaterialManager = Managers.MaterialManager(self)

        with self.Bind():
            self._camera: Abc.Camera = Camera(
                self,
                resolution=self.size,
                projection={
                    'type': 'orthographic',
                },
            )

            self.SetVSync(self.vsync)
            GL.Enable('multisample')

        glfw.set_window_size_callback(self.glfw_window, self._SizeCallback)

        self._should_close: bool = False
        self._closed: bool = False
        glfw.set_window_close_callback(self.glfw_window, self._CloseCallback)

        if visible:
            self.visible = True

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        with self.Bind():
            self.input_manager.Dispose()
            self.shader_manager.Dispose()
            self.material_manager.Dispose()
            self.camera.Dispose()

        GL.Window.Delete(self.glfw_window)
        self._window = None

    def _SizeCallback(self, window: GL.Window.GLFWWindow, width: int, height: int):
        self.on_resize.Invoke(self, Types.Vec2(width, height))

    def _CloseCallback(self, window: GL.Window.GLFWWindow):
        self.Close()

    @stopwatch
    def Simulate(self):
        self.on_simulate.Invoke(self)

        if self._closed:
            return

        elif self._should_close:
            self._PerformClose()
            return

        with self.Bind():
            self.Simulation()
            GL.Window.SwapBuffers(self.glfw_window)

        self.on_simulated.Invoke(self)

    @stopwatch
    def Simulation(self):
        self.input_manager.Simulate()

        self.camera.Render()
        self.camera.Draw()

    def _PerformClose(self):
        self.on_close.Invoke(self)

        GL.Window.Close(self.glfw_window)
        self.visible = False

        self.on_closed.Invoke(self)
        self._closed = True

    def Close(self):
        if self._closed or self._should_close:
            return self
        self._should_close = True
        return self

    def GetID(self):
        return self._id

    def GetName(self):
        return self._name

    def GetVSync(self) -> GL.hints.vsync:
        return self._vsync

    def SetVSync(self, value: GL.hints.vsync):
        self._vsync = GL.Window.SetVsync(self.glfw_window, value)

    def GetGLFWWindow(self):
        return self._window

    @contextmanager
    def Bind(self):
        with GL.Window.Bind(self.glfw_window):
            yield self

    @property
    def shader_manager(self):
        return self._shader_manager

    @property
    def material_manager(self):
        return self._material_manager

    @property
    def input_manager(self):
        return self._input_manager

    @property
    def should_close(self) -> bool:
        return GL.Window.ShouldClose(self._window)

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def context_version(self) -> Types.hints.context_version:
        return self._context_version

    @property
    def double_buffer(self) -> bool:
        return self._double_buffer

    def GetCamera(self) -> Abc.Camera:
        return self._camera

    def SetCamera(self, value: Abc.Camera):
        self._camera, camera_prev = value, self._camera
        camera_prev.Dispose()

    def GetSize(self) -> Types.Vec2[int]:
        return Types.Vec2[int].New(glfw.get_window_size(self.glfw_window))

    def SetSize(self, value: Types.hints.size_2d):
        glfw.set_window_size(self.glfw_window, *value)

    def GetWidth(self) -> int:
        return self.GetSize()[0]

    def SetWidth(self, value: int):
        self.SetSize((value, self.GetHeight()))

    def GetHeight(self) -> int:
        return self.GetSize()[1]

    def SetHeight(self, value: int):
        self.SetSize((self.GetWidth(), value))

    def GetTitle(self) -> str:
        return glfw.get_window_title(self.glfw_window) or '?'

    def SetTitle(self, value: str):
        glfw.set_window_title(self.glfw_window, value)

    def GetVisible(self) -> bool:
        return glfw.get_window_attrib(self.glfw_window, glfw.VISIBLE)

    def SetVisible(self, value: bool):
        if value:
            glfw.show_window(self.glfw_window)
        else:
            glfw.hide_window(self.glfw_window)

    def GetResizable(self) -> bool:
        return glfw.get_window_attrib(self.glfw_window, glfw.RESIZABLE)

    def SetResizable(self, value: bool):
        glfw.set_window_attrib(self.glfw_window, glfw.RESIZABLE, value)

    def GetMaximized(self) -> bool:
        return glfw.get_window_attrib(self.glfw_window, glfw.MAXIMIZED)

    def SetMaximized(self, value: bool):
        glfw.set_window_attrib(self.glfw_window, glfw.MAXIMIZED, value)

    def GetDecorated(self) -> bool:
        return glfw.get_window_attrib(self.glfw_window, glfw.DECORATED)

    def SetDecorated(self, value: bool):
        glfw.set_window_attrib(self.glfw_window, glfw.DECORATED, value)

    def GetFloating(self) -> bool:
        return glfw.get_window_attrib(self.glfw_window, glfw.FLOATING)

    def SetFloating(self, value: bool):
        glfw.set_window_attrib(self.glfw_window, glfw.FLOATING, value)

    def SetBackgroundColor(self, value: Types.hints.rgb):
        self._background_color = Types.RGB[int](*value)

    def GetBackgroundColor(self):
        return self._background_color

    @property
    def on_simulate(self):
        return self._on_simulate

    @property
    def on_simulated(self):
        return self._on_simulated

    @property
    def on_close(self):
        return self._on_close

    @property
    def on_closed(self):
        return self._on_closed

    @property
    def on_resize(self):
        return self._on_resize
