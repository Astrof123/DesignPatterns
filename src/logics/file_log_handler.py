import datetime
import os
from typing import Dict, Optional
from src.core.log_formatter import LogFormatter
from src.core.log_handler import LogHandler, LogLevel


class FileLogHandler(LogHandler):
    """Обработчик логов для записи в файл"""
    
    def __init__(self, level: LogLevel, formatter: LogFormatter, log_dir: str = "logs"):
        super().__init__(level, formatter)
        self.log_dir = log_dir
        self.current_file = None
        
        # Создаем директорию для логов, если она не существует
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self._update_log_file()
    
    def _update_log_file(self):
        """Обновляет файл лога на текущий день"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.current_file = os.path.join(self.log_dir, f"log_{today}.log")
    
    def handle(self, level: LogLevel, source: str, message: str, data: Optional[Dict] = None):
        if self.should_log(level):
            # Проверяем, не изменился ли день
            self._update_log_file()
            
            log_message = self.formatter.format(level.name, source, message, data)
            
            with open(self.current_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")