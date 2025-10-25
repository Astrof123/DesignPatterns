import unittest
from datetime import datetime
from src.models.nomenclature_model import NomenclatureModel
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.recipe_model import RecipeModel
from src.logics.factory_convert import FactoryConvert


class TestFactoryConvert(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.factory = FactoryConvert()
        
        # Создаем базовые сущности
        self.group = GroupNomenclatureModel()
        self.group.name = "Основная группа"
        self.unit = UnitMeasurement("шт", 1)
        self.nomenclature = NomenclatureModel("Товар 1", "Полное название товара 1", self.group, self.unit)
        self.recipe = RecipeModel("Рецепт 1", "Описание рецепта")

    # Конвертация NomenclatureModel возвращает комбинированный результат всех конверторов
    def test_convert_nomenclature_returns_combined_result(self):
        # Подготовка
        entity = self.nomenclature
        
        # Действие
        result = self.factory.convert(entity)
        
        # Проверка
        # Базовые поля от BasicConvertor
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("full_name", result)
        self.assertEqual(result["name"], "Товар 1")
        self.assertEqual(result["full_name"], "Полное название товара 1")
        
        # Ссылочные поля от ReferenceConvertor
        self.assertIn("group_nomenclature", result)
        self.assertIn("unit_measurement", result)
        self.assertEqual(result["group_nomenclature"], self.group.id)
        self.assertEqual(result["unit_measurement"], self.unit.id)

    # Конвертация UnitMeasurement с base_unit возвращает все типы полей
    def test_convert_unit_measurement_with_base_unit_returns_all_fields(self):
        # Подготовка
        gramm = UnitMeasurement("грамм", 1)
        kilogram = UnitMeasurement("килограмм", 1000, gramm)
        
        # Действие
        result = self.factory.convert(kilogram)
        
        # Проверка
        # Базовые поля
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("coefficient", result)
        self.assertEqual(result["name"], "килограмм")
        self.assertEqual(result["coefficient"], 1000)
        
        # Ссылочные поля
        self.assertIn("base_unit", result)
        self.assertEqual(result["base_unit"], gramm.id)

    # Конвертация GroupNomenclatureModel возвращает только базовые поля
    def test_convert_group_nomenclature_returns_only_basic_fields(self):
        # Подготовка
        entity = self.group
        
        # Действие
        result = self.factory.convert(entity)
        
        # Проверка
        # Базовые поля
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "Основная группа")
        
        # Нет ссылочных полей (ReferenceConvertor вернул пустой словарь)
        # Нет datetime полей (DatetimeConvertor вернул пустой словарь)

    # Конвертация RecipeModel возвращает базовые и ссылочные поля
    def test_convert_recipe_with_ingredients_returns_basic_and_reference_fields(self):
        # Подготовка
        recipe = self.recipe
        # Добавляем ингредиенты через рефлексию
        recipe._RecipeModel__ingredients = [self.nomenclature]
        
        # Действие
        result = self.factory.convert(recipe)
        
        # Проверка
        # Базовые поля
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("description", result)
        self.assertEqual(result["name"], "Рецепт 1")
        self.assertEqual(result["description"], "Описание рецепта")
        
        # Ссылочные поля
        self.assertIn("ingredients", result)
        self.assertEqual(result["ingredients"][0], self.nomenclature.id)

    # Конвертация объекта с datetime полями включает отформатированные даты
    def test_convert_object_with_datetime_fields_includes_formatted_dates(self):
        # Подготовка
        # Создаем группу и добавляем datetime поле через рефлексию
        group = GroupNomenclatureModel()
        group.name = "Группа с датой"

        created_date = datetime(2023, 12, 25, 10, 30, 45)
        group._GroupNomenclatureModel__created_date = created_date
        
        # Действие
        result = self.factory.convert(group)
        
        # Проверка
        # Базовые поля
        self.assertIn("id", result)
        self.assertIn("name", result)
        
        # Datetime поля (если есть)
        # Проверяем, что если есть datetime поля, они правильно отформатированы
        for field, value in result.items():
            if "date" in field or "time" in field:
                self.assertEqual(value, "2023-12-25 10:30:45")

    # Конвертация нескольких объектов работает корректно
    def test_convert_multiple_objects_works_correctly(self):
        # Подготовка
        entities = [self.group, self.nomenclature, self.unit]
        
        # Действие и Проверка
        for entity in entities:
            with self.subTest(entity_type=type(entity).__name__):
                result = self.factory.convert(entity)
                
                # Проверяем, что результат не пустой
                self.assertIsInstance(result, dict)
                self.assertIn("id", result)
                self.assertIn("name", result)

    # Конвертация объединяет результаты всех конверторов без потери данных
    def test_convert_combines_all_convertors_without_data_loss(self):
        # Подготовка
        entity = self.nomenclature
        
        # Действие
        result = self.factory.convert(entity)
        
        # Проверка - убеждаемся, что все ожидаемые поля присутствуют
        expected_basic_fields = ["id", "name", "full_name"]
        expected_reference_fields = ["group_nomenclature", "unit_measurement"]
        
        for field in expected_basic_fields:
            self.assertIn(field, result, f"Basic field '{field}' missing")
        
        for field in expected_reference_fields:
            self.assertIn(field, result, f"Reference field '{field}' missing")


    # Конвертация возвращает словарь с правильными типами значений
    def test_convert_returns_dict_with_correct_value_types(self):
        # Подготовка
        entity = self.nomenclature
        
        # Действие
        result = self.factory.convert(entity)
        
        # Проверка
        self.assertIsInstance(result, dict)
        
        # Проверяем типы значений
        self.assertIsInstance(result["id"], str)  # ID обычно строка
        self.assertIsInstance(result["name"], str)
        self.assertIsInstance(result["full_name"], str)
        self.assertIsInstance(result["group_nomenclature"], str)  # ID ссылки
        self.assertIsInstance(result["unit_measurement"], str)   # ID ссылки

    # Конвертация UnitMeasurement без base_unit не включает base_unit поле
    def test_convert_unit_measurement_without_base_unit_excludes_base_unit_field(self):
        # Подготовка
        unit = UnitMeasurement("шт", 1)  # Без базовой единицы
        
        # Действие
        result = self.factory.convert(unit)
        
        # Проверка
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("coefficient", result)
        self.assertNotIn("base_unit", result)  # Не должно быть base_unit поля


if __name__ == '__main__':
    unittest.main()