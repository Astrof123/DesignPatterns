from enum import Enum
from typing import Dict, Optional

from src.core.log_formatter import LogFormatter

class LogLevel(Enum):
    """Уровни логирования"""
    ERROR = 1
    INFO = 2
    DEBUG = 3


class LogMode(Enum):
    """Режимы логирования"""
    CONSOLE = "console"
    FILE = "file"
    BOTH = "both"


class LogHandler:
    """Базовый обработчик логов"""
    
    def __init__(self, level: LogLevel, formatter: LogFormatter):
        self.level = level
        self.formatter = formatter
    
    def should_log(self, log_level: LogLevel) -> bool:
        """Проверяет, нужно ли логировать сообщение данного уровня"""
        return log_level.value <= self.level.value
    
    def handle(self, level: LogLevel, source: str, message: str, data: Optional[Dict] = None):
        """Обрабатывает лог-сообщение (должен быть переопределен)"""
        raise NotImplementedError