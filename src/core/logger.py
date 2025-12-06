from typing import Dict, List, Optional

from src.core.log_formatter import LogFormatter
from src.core.log_handler import LogHandler, LogLevel, LogMode
from src.logics.console_log_handler import ConsoleLogHandler
from src.logics.file_log_handler import FileLogHandler


class Logger:
    """Основной класс логирования (аналог ObserveService)"""
    
    handlers: List[LogHandler] = []
    current_level: LogLevel = LogLevel.INFO
    current_mode: LogMode = LogMode.CONSOLE
    formatter: LogFormatter = LogFormatter()
    log_dir: str = "logs"
    
    @staticmethod
    def configure(level: str, mode: str, date_format: str = None, 
                  log_format: str = None, log_dir: str = None):
        """Настраивает систему логирования"""
        # Устанавливаем уровень
        if level.upper() == "DEBUG":
            Logger.current_level = LogLevel.DEBUG
        elif level.upper() == "INFO":
            Logger.current_level = LogLevel.INFO
        elif level.upper() == "ERROR":
            Logger.current_level = LogLevel.ERROR
        
        # Устанавливаем режим
        if mode.lower() == "file":
            Logger.current_mode = LogMode.FILE
        elif mode.lower() == "both":
            Logger.current_mode = LogMode.BOTH
        else:
            Logger.current_mode = LogMode.CONSOLE
        
        # Обновляем форматтер
        if date_format or log_format:
            Logger.formatter = LogFormatter(
                date_format=date_format or Logger.formatter.date_format,
                log_format=log_format or Logger.formatter.log_format
            )
        
        # Обновляем директорию логов
        if log_dir:
            Logger.log_dir = log_dir
        
        # Очищаем существующие обработчики
        Logger.handlers.clear()
        
        # Создаем обработчики в зависимости от режима
        if Logger.current_mode == LogMode.CONSOLE:
            handler = ConsoleLogHandler(Logger.current_level, Logger.formatter)
            Logger.handlers.append(handler)
        elif Logger.current_mode == LogMode.FILE:
            handler = FileLogHandler(Logger.current_level, Logger.formatter, Logger.log_dir)
            Logger.handlers.append(handler)
        elif Logger.current_mode == LogMode.BOTH:
            # Добавляем оба обработчика
            console_handler = ConsoleLogHandler(Logger.current_level, Logger.formatter)
            file_handler = FileLogHandler(Logger.current_level, Logger.formatter, Logger.log_dir)
            Logger.handlers.append(console_handler)
            Logger.handlers.append(file_handler)
    
    @staticmethod
    def log(level: LogLevel, source: str, message: str, data: Optional[Dict] = None):
        """Создает запись в логе"""
        for handler in Logger.handlers:
            handler.handle(level, source, message, data)
    
    @staticmethod
    def error(source: str, message: str, data: Optional[Dict] = None):
        """Логирование уровня ERROR"""
        Logger.log(LogLevel.ERROR, source, message, data)
    
    @staticmethod
    def info(source: str, message: str, data: Optional[Dict] = None):
        """Логирование уровня INFO"""
        if Logger.current_level.value >= LogLevel.INFO.value:
            Logger.log(LogLevel.INFO, source, message, data)
    
    @staticmethod
    def debug(source: str, message: str, data: Optional[Dict] = None):
        """Логирование уровня DEBUG"""
        if Logger.current_level.value >= LogLevel.DEBUG.value:
            Logger.log(LogLevel.DEBUG, source, message, data)
    
    @staticmethod
    def warning(source: str, message: str, data: Optional[Dict] = None):
        """Логирование уровня WARNING (используем INFO как уровень)"""
        if Logger.current_level.value >= LogLevel.INFO.value:
            # Форматируем как WARNING, но используем уровень INFO
            Logger.log(LogLevel.INFO, source, f"WARNING: {message}", data)
    
    @staticmethod
    def log_api_request(method: str, endpoint: str, data: Optional[Dict] = None):
        """Логирование API запросов"""
        message = f"API Request: {method} {endpoint}"
        log_data = {"method": method, "endpoint": endpoint}
        
        if data and method.upper() in ["DELETE", "PUT", "PATCH"]:
            log_data["request_data"] = data
        
        Logger.info("API", message, log_data)