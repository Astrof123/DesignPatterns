from typing import Dict, Optional
from src.core.log_formatter import LogFormatter
from src.core.log_handler import LogHandler, LogLevel


class ConsoleLogHandler(LogHandler):
    """Обработчик логов для вывода в консоль"""
    
    def __init__(self, level: LogLevel, formatter: LogFormatter):
        super().__init__(level, formatter)
    
    def handle(self, level: LogLevel, source: str, message: str, data: Optional[Dict] = None):
        if self.should_log(level):
            log_message = self.formatter.format(level.name, source, message, data)
            print(log_message)