import json
import unittest
import os
import xml.etree.ElementTree as ET

from src.logics.response_json import ResponseJson
from src.logics.response_markdown import ResponseMarkdown
from src.logics.response_xml import ResponseXml
from src.models.nomenclature_model import NomenclatureModel
from src.models.recipe_model import RecipeModel
from src.models.unit_measurement_model import UnitMeasurement
from src.logics.response_csv import ResponseCsv
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.logics.factory_entities import FactoryEntities
from src.core.response_format import ResponseFormats
from src.core.validator import Validator
from src.core.abstract_response import AbstractResponse


class TestLogics(unittest.TestCase):

    # Подготовка тестовых данных
    def setUp(self):
        
        # Подготовка
        self.test_output_dir = "tests/test_output"
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)
        
        self.group = GroupNomenclatureModel()
        self.group.name = "Основная группа"
        
        self.unit = UnitMeasurement("шт", 1)
        self.unit.name = "Штука"
        
        self.nomenclature1 = NomenclatureModel("Товар 1", "Полное название товара 1", self.group, self.unit)
        self.nomenclature2 = NomenclatureModel("Товар 2", "Полное название товара 2", self.group, self.unit)
        
        self.recipe = RecipeModel("Рецепт 1", "Описание рецепта")

    # Вспомогательный метод для сохранения данных в файл
    def save_to_file(self, content, filename):
        filepath = os.path.join(self.test_output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        return filepath

    # Проверка формирования CSV с любыми данными возвращает не None
    def test_build_csv_format_any_data_returns_not_none(self):
        # Подготовка
        response = ResponseCsv()
        data = []
        entity = GroupNomenclatureModel.create("test")
        data.append(entity)
        
        # Действие
        result = response.build("csv", data)
        
        # Проверка
        assert result is not None

    # Создание фабрики с валидным форматом возвращает экземпляр ответа
    def test_create_factory_valid_format_returns_response_instance(self):
        # Подготовка
        factory = FactoryEntities()
        data = []
        entity = GroupNomenclatureModel.create("test")
        data.append(entity)

        # Действие
        logic = factory.create(ResponseFormats.csv())
        instance = logic()
        text = instance.build(ResponseFormats.csv(), data)

        # Проверка
        assert logic is not None
        Validator.validate(instance, AbstractResponse)
        assert len(text) > 0

    # Формирование номенклатуры в CSV содержит обязательные поля
    def test_build_nomenclature_csv_format_contains_required_fields(self):
        # Подготовка
        response = ResponseCsv()
        data = [self.nomenclature1, self.nomenclature2]
        
        # Действие
        result = response.build("CSV", data)
        filename = "nomenclature.csv"
        filepath = self.save_to_file(result, filename)
        
        # Проверка
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("full_name", result)
        self.assertIn("Товар 1", result)
        self.assertIn("Полное название товара 1", result)

    # Формирование номенклатуры в Markdown создает валидную таблицу
    def test_build_nomenclature_markdown_format_creates_valid_table(self):
        # Подготовка
        response = ResponseMarkdown()
        data = [self.nomenclature1]
        
        # Действие
        result = response.build("Markdown", data)
        filename = "nomenclature.md"
        filepath = self.save_to_file(result, filename)
        
        # Проверка
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
        self.assertIn("| id | name |", result)
        self.assertIn("| Полное название товара 1 | Основная группа |", result)

    # Формирование номенклатуры в JSON создает валидный JSON
    def test_build_nomenclature_json_format_creates_valid_json(self):
        # Подготовка
        response = ResponseJson()
        data = [self.nomenclature1]
        
        # Действие
        result = response.build("Json", data)
        filename = "nomenclature.json"
        filepath = self.save_to_file(result, filename)
        
        # Проверка
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["name"], "Товар 1")
        self.assertEqual(parsed[0]["full_name"], "Полное название товара 1")

    # Формирование номенклатуры в XML содержит обязательные теги
    def test_build_nomenclature_xml_format_contains_required_tags(self):
        # Подготовка
        response = ResponseXml()
        data = [self.nomenclature1]
        
        # Действие
        result = response.build("XML", data)
        filename = "nomenclature.xml"
        filepath = self.save_to_file(result, filename)
        
        # Проверка
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
        self.assertIn("<name>Товар 1</name>", result)
        self.assertIn("<full_name>Полное название товара 1</full_name>", result)

    # Формирование группы номенклатуры в JSON содержит данные группы
    def test_build_group_nomenclature_json_format_contains_group_data(self):
        # Подготовка
        response = ResponseJson()
        data = [self.group]
        
        # Действие
        result = response.build("Json", data)
        filename = "group_nomenclature.json"
        filepath = self.save_to_file(result, filename)
        
        # Проверка
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
        parsed = json.loads(result)
        self.assertEqual(parsed[0]["name"], "Основная группа")

    # Формирование единицы измерения в JSON содержит данные единицы
    def test_build_unit_measurement_json_format_contains_unit_data(self):
        # Подготовка
        response = ResponseJson()
        data = [self.unit]
        
        # Действие
        result = response.build("Json", data)
        filename = "unit_measurement.json"
        filepath = self.save_to_file(result, filename)
        
        # Проверка
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
        parsed = json.loads(result)
        self.assertEqual(parsed[0]["name"], "Штука")
        self.assertEqual(parsed[0]["coefficient"], "1")

    # Формирование рецепта в JSON содержит данные рецепта
    def test_build_recipe_json_format_contains_recipe_data(self):
        # Подготовка
        response = ResponseJson()
        data = [self.recipe]
        
        # Действие
        result = response.build("Json", data)
        filename = "recipe.json"
        filepath = self.save_to_file(result, filename)
        
        # Проверка
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
        parsed = json.loads(result)
        self.assertEqual(parsed[0]["name"], "Рецепт 1")
        self.assertEqual(parsed[0]["description"], "Описание рецепта")

    # Генерация всех форматов для всех сущностей создает валидные файлы
    def test_generate_all_formats_all_entities_creates_valid_files(self):
        # Подготовка
        formats = ["csv", "markdown", "json", "xml"]
        entities = {
            "groups": [self.group],
            "units": [self.unit],
            "nomenclature": [self.nomenclature1, self.nomenclature2],
            "recipes": [self.recipe]
        }
        factory = FactoryEntities()
        
        # Действие и Проверка
        for entity_name, entity_data in entities.items():
            for format_name in formats:
                with self.subTest(entity=entity_name, format=format_name):
                    # Действие
                    response_class = factory.create(format_name)
                    response_instance = response_class()
                    result = response_instance.build(format_name, entity_data)
                    
                    extension = {
                        "csv": "csv",
                        "markdown": "md", 
                        "json": "json",
                        "xml": "xml"
                    }[format_name]
                    
                    filename = f"{entity_name}.{extension}"
                    filepath = self.save_to_file(result, filename)
                    
                    # Проверка
                    self.assertTrue(os.path.exists(filepath))
                    self.assertGreater(os.path.getsize(filepath), 0)
                    
                    if format_name == "json":
                        json.loads(result)
                    elif format_name == "xml":
                        ET.fromstring(result)

    # Валидация содержимого файлов всех форматов содержит ожидаемые данные
    def test_validate_file_content_all_formats_contains_expected_data(self):
        # Подготовка
        formats = {
            "csv": ResponseCsv(),
            "md": ResponseMarkdown(), 
            "json": ResponseJson(),
            "xml": ResponseXml()
        }
        data = [self.nomenclature1]
        
        # Действие и Проверка
        for extension, response in formats.items():
            with self.subTest(format=extension):
                format_name = extension.upper() if extension != "md" else "Markdown"
                result = response.build(format_name, data)
                filename = f"validation_test_nomenclature.{extension}"
                filepath = self.save_to_file(result, filename)
                
                # Проверка
                if extension == "csv":
                    self.assertIn("name", result)
                    self.assertIn("Товар 1", result)
                elif extension == "md":
                    self.assertIn("|", result)
                    self.assertIn("Товар 1", result)
                elif extension == "json":
                    parsed = json.loads(result)
                    self.assertEqual(parsed[0]["name"], "Товар 1")
                elif extension == "xml":
                    self.assertIn("<name>Товар 1</name>", result)


if __name__ == '__main__':
    unittest.main()