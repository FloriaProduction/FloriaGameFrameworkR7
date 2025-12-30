import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from . import Types, GL


@dataclass
class ConfigCls:
    PIX: int = 32
    '''пикселей в единице измерения'''

    FPS: int = 300
    '''Максимум кадров в секунду'''
    SPS: int = 20
    '''Максимум симуляций(тиков) в секунду'''
    TPS: int = 1000
    '''Максимум обновлений таймеров в секунду'''

    VSYNC: 'GL.hints.vsync' = 'full'
    '''Общая настройка вертикальной синхронизация для окон. Может переназначаться в конструкторе определенного окна.'''

    SHOW_SWITCHER_OUTPUT: bool = False
    '''Выводить информацию о переключении OpenGL-контекстов.'''

    LOG_TERMINAL_FORMAT: str = '[%(levelname)s]  %(asctime)s.%(msecs)03d  %(name)s:\t%(message)s'
    LOG_FILE_FORMAT: str = '[%(levelname)s]  %(asctime)s.%(msecs)03d  %(name)s:\t%(message)s'
    LOG_FILE_MODE: t.Literal['r', 'a'] = 'a'

    GAME_CYCLE_MODE: t.Literal['concurent', 'sync'] = 'sync'
    '''Тип цикла ядра.
    
    Args:
        sync: Запускает один цикл, который последовательно обновляет отрисовку, симуляцию и таймеры.
        councurent: Запускает 3 асинхронных задачи, которые конкурентно обновляют отрисовку, симуляцию и таймеры.
    '''

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
    '''Версия OpenGL. `Настоятельно не рекомендуется менять.`'''

    CANCEL_TASK_TIMEOUT: float = 5
    '''Количество секунд ожидания завершения асинхронных задач во время завершения ядра.'''


Config: t.Final[ConfigCls] = ConfigCls()
