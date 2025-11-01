import unittest
import os
import json
from src.data_manager import DataManager
from src.logics.factory_entities import FactoryEntities
from src.repository import Repository
from src.start_service import StartService


class TestDataManager(unittest.TestCase):
    __data_manager: DataManager = DataManager()
    __factory: FactoryEntities = FactoryEntities()
    __start_service: StartService = StartService()
    
    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.__start_service.start(True)
        self.test_filename = "test_data.json"
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
        if os.path.exists("data"):
            import shutil
            shutil.rmtree("data")

    def test_create_data_manager_instance_created(self):
        # Подготовка & Действие
        manager1 = DataManager()
        manager2 = DataManager()

        # Проверка
        assert isinstance(manager1, DataManager)
        assert isinstance(manager2, DataManager)

    def test_prepare_data_returns_correct_structure(self):
        # Подготовка
        data = self.__start_service.data

        # Действие
        result = self.__data_manager.prepare_data(data, self.__factory)

        # Проверка
        assert result is not None
        assert isinstance(result, dict)
        # Проверяем, что все ключи из репозитория присутствуют
        all_fields = Repository.get_key_fields(Repository)
        for field in all_fields:
            assert field in result

    def test_prepare_data_contains_json_format(self):
        # Подготовка
        data = self.__start_service.data

        # Действие
        result = self.__data_manager.prepare_data(data, self.__factory)

        # Проверка
        for field in result:
            assert isinstance(result[field], (list, dict, str))

    def test_save_data_to_file_creates_file(self):
        # Подготовка
        data = self.__start_service.data

        # Действие
        result = self.__data_manager.save_data_to_file(data, self.__factory, self.test_filename)

        # Проверка
        assert result is True
        assert os.path.exists(self.test_filename)

    def test_save_data_to_file_writes_correct_content(self):
        # Подготовка
        data = self.__start_service.data

        # Действие
        self.__data_manager.save_data_to_file(data, self.__factory, self.test_filename)

        # Проверка
        with open(self.test_filename, 'r', encoding='utf-8') as file:
            content = json.load(file)
        
        # Проверяем структуру файла
        all_fields = Repository.get_key_fields(Repository)
        for field in all_fields:
            assert field in content

    def test_save_data_to_file_creates_directory_if_not_exists(self):
        # Подготовка
        data = self.__start_service.data
        nested_filename = "non_existent_dir/test_data.json"

        # Действие
        result = self.__data_manager.save_data_to_file(data, self.__factory, nested_filename)

        # Проверка
        assert result is True
        assert os.path.exists(nested_filename)

    def test_save_data_to_file_returns_false_on_error(self):
        # Подготовка
        data = self.__start_service.data
        # Попытка записи в невалидный путь
        invalid_filename = "/invalid_path/data.json"

        # Действие
        result = self.__data_manager.save_data_to_file(data, self.__factory, invalid_filename)

        # Проверка
        assert result is False

    def test_save_data_to_file_default_filename(self):
        # Подготовка
        data = self.__start_service.data
        default_filename = "data/data.json"

        # Действие
        result = self.__data_manager.save_data_to_file(data, self.__factory)

        # Проверка
        assert result is True
        assert os.path.exists(default_filename)

    def test_prepare_data_handles_empty_data(self):
        # Подготовка
        empty_data = {}

        # Действие
        result = self.__data_manager.prepare_data(empty_data, self.__factory)

        # Проверка
        assert result is not None
        assert isinstance(result, dict)

    def test_save_and_load_cycle_data_integrity(self):
        # Подготовка
        data = self.__start_service.data

        # Действие - сохраняем
        self.__data_manager.save_data_to_file(data, self.__factory, self.test_filename)
        
        # Действие - загружаем обратно
        with open(self.test_filename, 'r', encoding='utf-8') as file:
            loaded_data = json.load(file)

        # Проверка
        prepared_data = self.__data_manager.prepare_data(data, self.__factory)
        assert loaded_data == prepared_data

    def test_prepare_data_field_values_are_serializable(self):
        # Подготовка
        data = self.__start_service.data

        # Действие
        prepared_data = self.__data_manager.prepare_data(data, self.__factory)

        # Проверка - пытаемся сериализовать каждый элемент
        for field, value in prepared_data.items():
            try:
                json.dumps(value)
            except TypeError as e:
                self.fail(f"Field {field} contains non-serializable data: {e}")