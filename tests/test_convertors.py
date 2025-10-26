import unittest
from datetime import datetime
from src.core.abstract_model import AbstractModel
from src.models.nomenclature_model import NomenclatureModel
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.recipe_model import RecipeModel
from src.logics.datetime_convertor import DatetimeConvertor
from src.logics.reference_convertor import ReferenceConvertor
from src.logics.basic_convertor import BasicConvertor
from src.core.validator import ArgumentException


class TestConvertors(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем базовые сущности
        self.group = GroupNomenclatureModel()
        self.group.name = "Основная группа"
        self.unit = UnitMeasurement("шт", 1)
        self.nomenclature = NomenclatureModel("Товар 1", "Полное название товара 1", self.group, self.unit)
        self.recipe = RecipeModel("Рецепт 1", "Описание рецепта")
        
        self.datetime_convertor = DatetimeConvertor()
        self.reference_convertor = ReferenceConvertor()
        self.basic_convertor = BasicConvertor()

    # Тесты для DatetimeConvertor

    # Конвертация datetime объекта возвращает строку в правильном формате
    def test_convert_datetime_returns_correct_format(self):
        # Подготовка
        test_datetime = datetime(2023, 10, 15, 14, 30, 45)
        
        # Действие
        result = self.datetime_convertor.convert(test_datetime)
        
        # Проверка
        self.assertEqual(result, "2023-10-15 14:30:45")

    # Конвертация не-datetime объекта вызывает исключение
    def test_convert_non_datetime_raises_exception(self):
        # Подготовка
        invalid_obj = "not a datetime"
        
        # Действие и Проверка
        with self.assertRaises(ArgumentException):
            self.datetime_convertor.convert(invalid_obj)

    # Конвертация различных datetime объектов работает корректно
    def test_convert_various_datetime_objects_works_correctly(self):
        # Подготовка
        test_cases = [
            datetime(2023, 1, 1, 0, 0, 0),
            datetime(2024, 12, 31, 23, 59, 59),
            datetime(2000, 6, 15, 12, 30, 0)
        ]
        
        expected_results = [
            "2023-01-01 00:00:00",
            "2024-12-31 23:59:59", 
            "2000-06-15 12:30:00"
        ]
        
        # Действие и Проверка
        for i, test_datetime in enumerate(test_cases):
            with self.subTest(datetime=test_datetime):
                result = self.datetime_convertor.convert(test_datetime)
                self.assertEqual(result, expected_results[i])

    # Тесты для ReferenceConvertor

    # Конвертация AbstractModel объекта возвращает его ID
    def test_convert_abstract_model_returns_id(self):
        # Подготовка
        entity = self.nomenclature
        
        # Действие
        result = self.reference_convertor.convert(entity)
        
        # Проверка
        self.assertEqual(result, entity.id)

    # Конвертация различных AbstractModel объектов возвращает их ID
    def test_convert_various_abstract_models_return_their_ids(self):
        # Подготовка
        test_entities = [self.group, self.unit, self.nomenclature, self.recipe]
        
        # Действие и Проверка
        for entity in test_entities:
            with self.subTest(entity_type=type(entity).__name__):
                result = self.reference_convertor.convert(entity)
                self.assertEqual(result, entity.id)

    # Конвертация не-AbstractModel объекта вызывает исключение
    def test_convert_non_abstract_model_raises_exception(self):
        # Подготовка
        invalid_obj = "not an abstract model"
        
        # Действие и Проверка
        with self.assertRaises(ArgumentException):
            self.reference_convertor.convert(invalid_obj)

    # Конвертация None объекта вызывает исключение
    def test_convert_none_raises_exception(self):
        # Подготовка
        invalid_obj = None
        
        # Действие и Проверка
        with self.assertRaises(ArgumentException):
            self.reference_convertor.convert(invalid_obj)

    # Тесты для BasicConvertor

    # Конвертация строки возвращает ту же строку
    def test_convert_string_returns_same_string(self):
        # Подготовка
        test_string = "test string"
        
        # Действие
        result = self.basic_convertor.convert(test_string)
        
        # Проверка
        self.assertEqual(result, test_string)

    # Конвертация целого числа возвращает то же число
    def test_convert_integer_returns_same_integer(self):
        # Подготовка
        test_int = 42
        
        # Действие
        result = self.basic_convertor.convert(test_int)
        
        # Проверка
        self.assertEqual(result, test_int)

    # Конвертация дробного числа возвращает то же число
    def test_convert_float_returns_same_float(self):
        # Подготовка
        test_float = 3.14
        
        # Действие
        result = self.basic_convertor.convert(test_float)
        
        # Проверка
        self.assertEqual(result, test_float)

    # Конвертация булевого значения возвращает то же значение
    def test_convert_boolean_returns_same_boolean(self):
        # Подготовка
        test_bool = True
        
        # Действие
        result = self.basic_convertor.convert(test_bool)
        
        # Проверка
        self.assertEqual(result, test_bool)

    # Конвертация не-базового типа вызывает исключение
    def test_convert_non_basic_type_raises_exception(self):
        # Подготовка
        invalid_obj = self.group  # AbstractModel, не базовый тип
        
        # Действие и Проверка
        with self.assertRaises(ArgumentException):
            self.basic_convertor.convert(invalid_obj)

    # Конвертация списка вызывает исключение
    def test_convert_list_raises_exception(self):
        # Подготовка
        invalid_obj = [1, 2, 3]
        
        # Действие и Проверка
        with self.assertRaises(ArgumentException):
            self.basic_convertor.convert(invalid_obj)

    # Конвертация None вызывает исключение
    def test_convert_none_basic_raises_exception(self):
        # Подготовка
        invalid_obj = None
        
        # Действие и Проверка
        with self.assertRaises(ArgumentException):
            self.basic_convertor.convert(invalid_obj)

    # Интеграционные тесты - проверка корректности работы валидации

    # Все конверторы корректно проверяют типы входных данных
    def test_all_convertors_validate_input_types_correctly(self):
        # Подготовка
        test_cases = [
            (self.basic_convertor, "test string", str, True),
            (self.basic_convertor, 123, int, True),
            (self.basic_convertor, self.group, AbstractModel, False),
            (self.reference_convertor, self.group, AbstractModel, True),
            (self.reference_convertor, "string", AbstractModel, False),
            (self.datetime_convertor, datetime.now(), datetime, True),
            (self.datetime_convertor, "2023-01-01", datetime, False)
        ]
        
        # Действие и Проверка
        for convertor, test_obj, expected_type, should_succeed in test_cases:
            with self.subTest(convertor=type(convertor).__name__, obj_type=type(test_obj).__name__):
                if should_succeed:
                    result = convertor.convert(test_obj)
                    self.assertIsNotNone(result)
                else:
                    with self.assertRaises(ArgumentException):
                        convertor.convert(test_obj)


if __name__ == '__main__':
    unittest.main()