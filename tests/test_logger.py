import json
import unittest
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch

from src.core.logger import Logger, LogLevel, LogMode, LogFormatter


class TestLogger(unittest.TestCase):

    # Подготовка тестовых данных
    def setUp(self):
        # Создаем временную директорию для тестов
        self.test_output_dir = tempfile.mkdtemp()
        self.test_log_dir = os.path.join(self.test_output_dir, "logs")
        
        # Сбрасываем состояние Logger перед каждым тестом
        Logger.handlers.clear()
        Logger.current_level = LogLevel.INFO
        Logger.current_mode = LogMode.CONSOLE
        Logger.formatter = LogFormatter()
        Logger.log_dir = "logs"
        
    # Очистка после тестов
    def tearDown(self):
        # Удаляем временную директорию
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    # Вспомогательный метод для проверки существования и чтения лог-файла
    def read_log_file(self, log_dir=None):
        if log_dir is None:
            log_dir = self.test_log_dir
            
        # Ищем файл лога за сегодняшний день
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"log_{today}.log")
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    # Конфигурация Logger с валидными параметрами создает обработчики
    def test_configure_logger_valid_params_creates_handlers(self):
        # Подготовка
        test_cases = [
            ("INFO", "console", 1, "ConsoleLogHandler"),
            ("DEBUG", "file", 1, "FileLogHandler"),
            ("ERROR", "both", 2, ["ConsoleLogHandler", "FileLogHandler"])
        ]
        
        for level, mode, expected_count, expected_handler in test_cases:
            with self.subTest(level=level, mode=mode):
                # Действие
                Logger.configure(level, mode, log_dir=self.test_log_dir)
                
                # Проверка
                self.assertEqual(len(Logger.handlers), expected_count)
                if isinstance(expected_handler, list):
                    handler_names = [type(h).__name__ for h in Logger.handlers]
                    for handler in expected_handler:
                        self.assertIn(handler, handler_names)
                else:
                    self.assertEqual(type(Logger.handlers[0]).__name__, expected_handler)
    
    # Логирование с уровнем DEBUG записывает сообщение при соответствующем уровне
    def test_log_debug_level_writes_message_when_level_configured(self):
        # Подготовка
        Logger.configure("DEBUG", "file", log_dir=self.test_log_dir)
        
        # Действие
        Logger.debug("TestSource", "Test debug message", {"key": "value"})
        
        # Проверка
        log_content = self.read_log_file()
        self.assertIsNotNone(log_content)
        self.assertIn("DEBUG", log_content)
        self.assertIn("TestSource", log_content)
        self.assertIn("Test debug message", log_content)
    
    # Логирование с уровнем INFO не записывает DEBUG сообщения при уровне INFO
    def test_log_info_level_does_not_write_debug_messages_when_level_info(self):
        # Подготовка
        Logger.configure("INFO", "file", log_dir=self.test_log_dir)
        
        # Действие
        Logger.debug("TestSource", "This debug message should not appear")
        Logger.info("TestSource", "This info message should appear")
        
        # Проверка
        log_content = self.read_log_file()
        self.assertIsNotNone(log_content)
        self.assertNotIn("This debug message should not appear", log_content)
        self.assertIn("This info message should appear", log_content)
    
    # Логирование с уровнем ERROR не записывает INFO и DEBUG сообщения
    def test_log_error_level_does_not_write_info_debug_messages(self):
        # Подготовка
        Logger.configure("ERROR", "file", log_dir=self.test_log_dir)
        
        # Действие
        Logger.debug("TestSource", "Debug message")
        Logger.info("TestSource", "Info message")
        Logger.error("TestSource", "Error message")
        
        # Проверка
        log_content = self.read_log_file()
        self.assertIsNotNone(log_content)
        self.assertNotIn("Debug message", log_content)
        self.assertNotIn("Info message", log_content)
        self.assertIn("Error message", log_content)
    
    # Форматировщик логов создает корректную строку с данными
    def test_log_formatter_creates_correct_string_with_data(self):
        # Подготовка
        formatter = LogFormatter(
            date_format="%Y-%m-%d",
            log_format="{timestamp} | {level} | {source} | {message} | {data}"
        )
        
        # Действие
        result = formatter.format("INFO", "TestSource", "Test message", {"key": "value"})
        
        # Проверка
        self.assertIn("INFO", result)
        self.assertIn("TestSource", result)
        self.assertIn("Test message", result)
        self.assertIn('"key": "value"', result)
    
    # Форматировщик логов создает корректную строку без данных
    def test_log_formatter_creates_correct_string_without_data(self):
        # Подготовка
        formatter = LogFormatter(
            log_format="{timestamp} | {level} | {source} | {message} | {data}"
        )
        
        # Действие
        result = formatter.format("ERROR", "ErrorSource", "Error occurred")
        
        # Проверка
        self.assertIn("ERROR", result)
        self.assertIn("ErrorSource", result)
        self.assertIn("Error occurred", result)
        self.assertIn("{}", result)  # Пустые данные
    
    # Логирование API запросов включает данные запроса для DELETE/PUT/PATCH методов
    def test_log_api_request_includes_data_for_delete_put_patch_methods(self):
        # Подготовка
        test_cases = [
            ("DELETE", True),
            ("PUT", True),
            ("PATCH", True),
            ("GET", False),
            ("POST", False)
        ]
        
        for method, should_include_data in test_cases:
            with self.subTest(method=method):
                Logger.configure("INFO", "file", log_dir=self.test_log_dir)
                request_data = {"id": 123, "name": "Test"}
                
                # Действие
                Logger.log_api_request(method, "/api/test", request_data if should_include_data else None)
                
                # Проверка
                log_content = self.read_log_file()
                self.assertIsNotNone(log_content)
                self.assertIn(f"API Request: {method} /api/test", log_content)
                
                if should_include_data:
                    self.assertIn('"request_data"', log_content)
                else:
                    self.assertNotIn('"request_data"', log_content)
    
    # Режим BOTH создает и консольный и файловый обработчики
    def test_both_mode_creates_console_and_file_handlers(self):
        # Подготовка
        
        # Действие
        Logger.configure("INFO", "both", log_dir=self.test_log_dir)
        
        # Проверка
        self.assertEqual(len(Logger.handlers), 2)
        handler_types = [type(h).__name__ for h in Logger.handlers]
        self.assertIn("ConsoleLogHandler", handler_types)
        self.assertIn("FileLogHandler", handler_types)
    
    # Создание лог файла за текущий день при записи в файл
    def test_file_handler_creates_log_file_for_current_day(self):
        # Подготовка
        Logger.configure("INFO", "file", log_dir=self.test_log_dir)
        
        # Действие
        Logger.info("Test", "Test message")
        
        # Проверка
        today = datetime.now().strftime("%Y-%m-%d")
        expected_file = os.path.join(self.test_log_dir, f"log_{today}.log")
        self.assertTrue(os.path.exists(expected_file))
        
        # Проверяем содержимое
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Test message", content)
    
    # Логирование с пользовательским форматом даты использует указанный формат
    def test_logging_with_custom_date_format_uses_specified_format(self):
        # Подготовка
        custom_format = "%H:%M:%S"
        Logger.configure("INFO", "file", 
                        date_format=custom_format,
                        log_format="{timestamp} | {message}",
                        log_dir=self.test_log_dir)
        
        # Действие
        Logger.info("Test", "Test message")
        
        # Проверка
        log_content = self.read_log_file()
        self.assertIsNotNone(log_content)
        
        # Проверяем, что временная метка соответствует формату HH:MM:SS
        import re
        timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2})', log_content)
        self.assertIsNotNone(timestamp_match)
    
    # Логирование с пользовательским форматом сообщения использует указанный формат
    def test_logging_with_custom_message_format_uses_specified_format(self):
        # Подготовка
        custom_format = "[{level}] {source}: {message}"
        Logger.configure("INFO", "file", 
                        log_format=custom_format,
                        log_dir=self.test_log_dir)
        
        # Действие
        Logger.info("TestSource", "Test message")
        
        # Проверка
        log_content = self.read_log_file()
        self.assertIsNotNone(log_content)
        self.assertIn("[INFO] TestSource: Test message", log_content)
    
    # Метод get_current_mode возвращает текущий режим логирования
    def test_get_current_mode_returns_current_logging_mode(self):
        # Подготовка
        test_cases = ["console", "file", "both"]
        
        for mode in test_cases:
            with self.subTest(mode=mode):
                # Действие
                Logger.configure("INFO", mode, log_dir=self.test_log_dir)
                
                # Проверка
                self.assertEqual(Logger.get_current_mode(), mode)
    
    # Метод get_current_level возвращает текущий уровень логирования
    def test_get_current_level_returns_current_logging_level(self):
        # Подготовка
        test_cases = ["ERROR", "INFO", "DEBUG"]
        
        for level in test_cases:
            with self.subTest(level=level):
                # Действие
                Logger.configure(level, "console", log_dir=self.test_log_dir)
                
                # Проверка
                self.assertEqual(Logger.get_current_level(), level)
    
    # Метод get_active_handlers возвращает список активных обработчиков
    def test_get_active_handlers_returns_list_of_active_handlers(self):
        # Подготовка
        test_cases = [
            ("console", ["ConsoleLogHandler"]),
            ("file", ["FileLogHandler"]),
            ("both", ["ConsoleLogHandler", "FileLogHandler"])
        ]
        
        for mode, expected_handlers in test_cases:
            with self.subTest(mode=mode):
                # Действие
                Logger.configure("INFO", mode, log_dir=self.test_log_dir)
                active_handlers = Logger.get_active_handlers()
                
                # Проверка
                self.assertEqual(len(active_handlers), len(expected_handlers))
                for handler in expected_handlers:
                    self.assertIn(handler, active_handlers)
    
    # Логирование с помощью метода warning создает сообщение с префиксом WARNING
    def test_warning_method_creates_message_with_warning_prefix(self):
        # Подготовка
        Logger.configure("INFO", "file", log_dir=self.test_log_dir)
        
        # Действие
        Logger.warning("TestSource", "Warning message")
        
        # Проверка
        log_content = self.read_log_file()
        self.assertIsNotNone(log_content)
        self.assertIn("WARNING: Warning message", log_content)
    
    # Логирование с некорректными данными в data не вызывает исключение
    def test_logging_with_invalid_data_does_not_raise_exception(self):
        # Подготовка
        Logger.configure("INFO", "file", log_dir=self.test_log_dir)
        
        # Создаем объект, который не может быть сериализован в JSON
        class NonSerializable:
            def __repr__(self):
                raise Exception("Cannot serialize")
        
        invalid_data = {"obj": NonSerializable()}
        
        # Действие и Проверка (не должно вызывать исключение)
        try:
            Logger.info("Test", "Test message", invalid_data)
            log_content = self.read_log_file()
            self.assertIsNotNone(log_content)
            self.assertIn("Test message", log_content)
        except Exception as e:
            self.fail(f"Логирование с некорректными данными вызвало исключение: {e}")
    
    # Конфигурация с несуществующей директорией создает директорию
    def test_configure_with_nonexistent_directory_creates_directory(self):
        # Подготовка
        new_log_dir = os.path.join(self.test_output_dir, "new_logs")
        
        # Проверяем, что директории не существует
        self.assertFalse(os.path.exists(new_log_dir))
        
        # Действие
        Logger.configure("INFO", "file", log_dir=new_log_dir)
        Logger.info("Test", "Test message")
        
        # Проверка
        self.assertTrue(os.path.exists(new_log_dir))
        
        # Проверяем, что файл лога создан
        log_content = self.read_log_file(new_log_dir)
        self.assertIsNotNone(log_content)
    

    
    # Тест логирования с разными уровнями в режиме BOTH
    def test_logging_different_levels_in_both_mode(self):
        # Подготовка
        Logger.configure("DEBUG", "both", log_dir=self.test_log_dir)
        
        # Действие
        Logger.debug("DebugSource", "Debug message")
        Logger.info("InfoSource", "Info message")
        Logger.error("ErrorSource", "Error message")
        Logger.warning("WarningSource", "Warning message")
        
        # Проверка файла
        log_content = self.read_log_file()
        self.assertIsNotNone(log_content)
        self.assertIn("Debug message", log_content)
        self.assertIn("Info message", log_content)
        self.assertIn("Error message", log_content)
        self.assertIn("WARNING: Warning message", log_content)
        
        # Проверка всех уровней присутствуют
        self.assertIn("DEBUG", log_content)
        self.assertIn("INFO", log_content)
        self.assertIn("ERROR", log_content)


if __name__ == '__main__':
    unittest.main()