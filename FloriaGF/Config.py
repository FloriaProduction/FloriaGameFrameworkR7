import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from . import Types, GL


@dataclass
class ConfigCls:
    PIX: int = 32
    '''пикселей в единице измерения'''

    FPS: float = 300
    '''Максимум кадров в секунду. По умолчанию 300.'''
    SPS: float = 20
    '''Максимум симуляций(тиков) в секунду. По умолчанию 20.'''
    TPS: float = 1000
    '''Максимум обновлений таймеров в секунду. По умолчанию 1000.'''

    VSYNC: 'GL.hints.vsync' = 'full'
    '''Общая настройка вертикальной синхронизация для окон. Может переназначаться в конструкторе определенного окна. По умолчанию full.'''

    SHOW_SWITCHER_OUTPUT: bool = False
    '''Выводить информацию о переключении OpenGL-контекстов.'''

    LOG_TERMINAL_FORMAT: str = '[%(levelname)s]  %(asctime)s.%(msecs)03d  %(name)s:\t%(message)s'
    LOG_FILE_FORMAT: str = '[%(levelname)s]  %(asctime)s.%(msecs)03d  %(name)s:\t%(message)s'
    LOG_FILE_MODE: t.Literal['r', 'a'] = 'a'

    @property
    def PIX_scale(self) -> float:
        '''Единица измерения для одного пикселя'''
        return 1 / self.PIX

    @property
    def FPS_delay(self) -> float:
        return (1 / self.FPS) if self.FPS > 0 else 0

    @property
    def SPS_delay(self) -> float:
        return (1 / self.SPS) if self.SPS > 0 else 0

    @property
    def TPS_delay(self) -> float:
        return (1 / self.TPS) if self.TPS > 0 else 0

    CONTEXT_VERSIONS: 'Types.hints.context_version' = (4, 2)
    '''Версия OpenGL. По умолчанию (4, 2). `Настоятельно не рекомендуется менять.`'''

    CANCEL_TASK_TIMEOUT: float = 5
    '''Количество секунд ожидания завершения асинхронных задач во время завершения ядра.'''


Config: t.Final[ConfigCls] = ConfigCls()
