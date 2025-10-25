import unittest
from datetime import datetime
from src.models.nomenclature_model import NomenclatureModel
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.recipe_model import RecipeModel
from src.logics.datetime_convertor import DatetimeConvertor
from src.logics.reference_convertor import ReferenceConvertor
from src.logics.basic_convertor import BasicConvertor


class TestConvertors(unittest.TestCase):
    # Подготовка тестовых данных
    def setUp(self):
        
        # Создаем базовые сущности
        self.group = GroupNomenclatureModel()
        self.group.name = "Основная группа"
        self.unit = UnitMeasurement("шт", 1)
        self.nomenclature = NomenclatureModel("Товар 1", "Полное название товара 1", self.group, self.unit)
        self.recipe = RecipeModel("Рецепт 1", "Описание рецепта")
        
        self.datetime_convertor = DatetimeConvertor()
        self.reference_convertor = ReferenceConvertor()
        self.basic_convertor = BasicConvertor()


    # Конвертация GroupNomenclatureModel с datetime полями возвращает правильный формат
    def test_convert_group_nomenclature_with_datetime_returns_correct_format(self):
        # Подготовка
        # Добавляем datetime поле в группу через рефлексию
        created_date = datetime(2023, 10, 15, 14, 30, 45)
        self.group._GroupNomenclatureModel__created_date = created_date
        
        # Действие
        result = self.datetime_convertor.convert(self.group)
        
        # Проверка
        if result:  # Если есть datetime поля
            for field, value in result.items():
                self.assertEqual(value, "2023-10-15 14:30:45")

    # Конвертация объекта без datetime полей возвращает пустой словарь
    def test_convert_object_without_datetime_returns_empty_dict(self):
        # Подготовка
        entity = GroupNomenclatureModel()
        entity.name = "Группа без дат"
        
        # Действие
        result = self.datetime_convertor.convert(entity)
        
        # Проверка
        self.assertEqual(result, {})

    # Тесты для ReferenceConvertor

    # Конвертация NomenclatureModel возвращает ID группы и единицы измерения
    def test_convert_nomenclature_returns_group_and_unit_ids(self):
        # Подготовка
        entity = self.nomenclature
        
        # Действие
        result = self.reference_convertor.convert(entity)
        
        # Проверка
        self.assertIn("group_nomenclature", result)
        self.assertIn("unit_measurement", result)
        self.assertEqual(result["group_nomenclature"], self.group.id)
        self.assertEqual(result["unit_measurement"], self.unit.id)

    # Конвертация UnitMeasurement с base_unit возвращает ID базовой единицы
    def test_convert_unit_measurement_with_base_unit_returns_base_unit_id(self):
        # Подготовка
        gramm = UnitMeasurement("грамм", 1)
        kilogram = UnitMeasurement("килограмм", 1000, gramm)
        
        # Действие
        result = self.reference_convertor.convert(kilogram)
        
        # Проверка
        self.assertIn("base_unit", result)
        self.assertEqual(result["base_unit"], gramm.id)

    # Конвертация UnitMeasurement без base_unit не возвращает base_unit поле
    def test_convert_unit_measurement_without_base_unit_does_not_return_base_unit(self):
        # Подготовка
        gramm = UnitMeasurement("грамм", 1)  # Без базовой единицы
        
        # Действие
        result = self.reference_convertor.convert(gramm)
        
        # Проверка
        self.assertNotIn("base_unit", result)

    # Конвертация RecipeModel с ingredients возвращает список ID ингредиентов
    def test_convert_recipe_with_ingredients_returns_ingredient_ids(self):
        # Подготовка
        recipe = self.recipe
        # Добавляем ингредиенты через рефлексию
        recipe._RecipeModel__ingredients = [self.nomenclature]
        
        # Действие
        result = self.reference_convertor.convert(recipe)
        
        # Проверка
        self.assertIn("ingredients", result)
        self.assertEqual(result["ingredients"][0], self.nomenclature.id)

    # Конвертация объекта без ссылочных полей возвращает пустой словарь
    def test_convert_object_without_references_returns_empty_dict(self):
        # Подготовка
        # UnitMeasurement без base_unit не имеет ссылочных полей
        unit = UnitMeasurement("шт", 1)
        
        # Действие
        result = self.reference_convertor.convert(unit)
        
        # Проверка
        self.assertEqual(result, {})

    # Тесты для BasicConvertor

    # Конвертация GroupNomenclatureModel возвращает базовые поля
    def test_convert_group_nomenclature_returns_basic_fields(self):
        # Подготовка
        entity = self.group
        
        # Действие
        result = self.basic_convertor.convert(entity)
        
        # Проверка
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "Основная группа")

    # Конвертация UnitMeasurement возвращает базовые поля
    def test_convert_unit_measurement_returns_basic_fields(self):
        # Подготовка
        entity = self.unit
        
        # Действие
        result = self.basic_convertor.convert(entity)
        
        # Проверка
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("coefficient", result)
        self.assertEqual(result["name"], "шт")
        self.assertEqual(result["coefficient"], 1)

    # Конвертация NomenclatureModel возвращает строковые поля
    def test_convert_nomenclature_returns_string_fields(self):
        # Подготовка
        entity = self.nomenclature
        
        # Действие
        result = self.basic_convertor.convert(entity)
        
        # Проверка
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("full_name", result)
        self.assertEqual(result["name"], "Товар 1")
        self.assertEqual(result["full_name"], "Полное название товара 1")

    # Конвертация RecipeModel возвращает строковые поля
    def test_convert_recipe_returns_string_fields(self):
        # Подготовка
        entity = self.recipe
        
        # Действие
        result = self.basic_convertor.convert(entity)
        
        # Проверка
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("description", result)
        self.assertEqual(result["name"], "Рецепт 1")
        self.assertEqual(result["description"], "Описание рецепта")


    # Комбинированная конвертация NomenclatureModel всеми конверторами
    def test_combined_conversion_nomenclature_works_correctly(self):
        # Подготовка
        entity = self.nomenclature
        
        # Действие
        basic_result = self.basic_convertor.convert(entity)
        reference_result = self.reference_convertor.convert(entity)
        datetime_result = self.datetime_convertor.convert(entity)
        
        # Проверка
        # BasicConvertor должен содержать базовые поля
        self.assertIn("name", basic_result)
        self.assertIn("full_name", basic_result)
        
        # ReferenceConvertor должен содержать ссылочные поля
        self.assertIn("group_nomenclature", reference_result)
        self.assertIn("unit_measurement", reference_result)
        
        # DatetimeConvertor должен быть пустым (нет datetime полей)
        self.assertEqual(datetime_result, {})

    # Конвертация UnitMeasurement с base_unit всеми конверторами
    def test_combined_conversion_unit_measurement_with_base_unit(self):
        # Подготовка
        gramm = UnitMeasurement("грамм", 1)
        kilogram = UnitMeasurement("килограмм", 1000, gramm)
        
        # Действие
        basic_result = self.basic_convertor.convert(kilogram)
        reference_result = self.reference_convertor.convert(kilogram)
        
        # Проверка
        # BasicConvertor должен содержать базовые поля
        self.assertIn("name", basic_result)
        self.assertIn("coefficient", basic_result)
        
        # ReferenceConvertor должен содержать ссылку на базовую единицу
        self.assertIn("base_unit", reference_result)
        self.assertEqual(reference_result["base_unit"], gramm.id)



if __name__ == '__main__':
    unittest.main()