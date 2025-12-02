import unittest
from unittest.mock import patch
import datetime

from src.logics.reference_service import ReferenceService
from src.models.nomenclature_model import NomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.storage_model import StorageModel
from src.models.recipe_model import RecipeModel
from src.models.transaction_model import TransactionModel
from src.models.ingredient_model import IngredientModel
from src.repository import Repository
from src.core.validator import ArgumentException, OperationException
from src.core.observe_service import ObserveService
from src.core.event_type import EventType


class TestReferenceService(unittest.TestCase):
    """Тесты для ReferenceService"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем мок репозитория
        self.mock_repository_data = {
            Repository.nomenclature_key: {},
            Repository.unit_measure_key: {},
            Repository.group_nomenclature_key: {},
            Repository.storage_key: {},
            Repository.recipe_key: {},
            Repository.transaction_key: {},
            Repository.balances_key: []
        }
        
        # Создаем тестовые объекты
        self.group = GroupNomenclatureModel()
        self.group.id = "group-1"
        self.group.name = "Ингредиенты"
        
        self.unit = UnitMeasurement("грамм", 1)
        self.unit.id = "unit-1"
        self.unit.name = "Грамм"
        
        self.storage = StorageModel("Основной склад", "ул. Ленина 1")
        self.storage.id = "storage-1"
        
        self.nomenclature = NomenclatureModel(
            "Мука",
            "Пшеничная мука",
            self.group,
            self.unit
        )
        self.nomenclature.id = "nomenclature-1"
        
        # Добавляем тестовые данные в репозиторий
        self.mock_repository_data[Repository.group_nomenclature_key][self.group.id] = self.group
        self.mock_repository_data[Repository.unit_measure_key][self.unit.id] = self.unit
        self.mock_repository_data[Repository.storage_key][self.storage.id] = self.storage
        self.mock_repository_data[Repository.nomenclature_key][self.nomenclature.id] = self.nomenclature
        
        # Создаем экземпляр сервиса
        self.service = ReferenceService(self.mock_repository_data)
    
    def tearDown(self):
        """Очистка после тестов"""
        # Очищаем обработчики событий
        ObserveService.handlers.clear()
    
    
    def test_get_by_id_existing_item_returns_item(self):
        """Получение существующего элемента по ID возвращает элемент"""
        # Действие
        result = self.service.get_by_id(Repository.nomenclature_key, "nomenclature-1")
        
        # Проверка
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "nomenclature-1")
        self.assertEqual(result.name, "Мука")
    
    def test_get_by_id_nonexistent_item_returns_none(self):
        """Получение несуществующего элемента по ID возвращает None"""
        # Действие
        result = self.service.get_by_id(Repository.nomenclature_key, "nonexistent-id")
        
        # Проверка
        self.assertIsNone(result)
    
    def test_get_by_id_invalid_reference_type_raises_exception(self):
        """Получение элемента с неверным типом справочника вызывает исключение"""
        # Проверка
        with self.assertRaises(ArgumentException):
            self.service.get_by_id("invalid_type", "some-id")
    
    
    def test_add_new_item_success(self):
        """Добавление нового элемента успешно"""
        # Подготовка
        new_item = GroupNomenclatureModel()
        new_item.id = "new-group-1"
        new_item.name = "Новая группа"
        
        # Действие
        result_id = self.service.add(Repository.group_nomenclature_key, new_item)
        
        # Проверка
        self.assertEqual(result_id, "new-group-1")
        self.assertIn("new-group-1", self.mock_repository_data[Repository.group_nomenclature_key])
        self.assertEqual(
            self.mock_repository_data[Repository.group_nomenclature_key]["new-group-1"].name,
            "Новая группа"
        )
    
    def test_add_existing_id_raises_exception(self):
        """Добавление элемента с существующим ID вызывает исключение"""
        # Подготовка
        duplicate_item = GroupNomenclatureModel()
        duplicate_item.id = "group-1"  # Такой ID уже существует
        duplicate_item.name = "Дубликат"
        
        # Проверка
        with self.assertRaises(ArgumentException):
            self.service.add(Repository.group_nomenclature_key, duplicate_item)
    
    
    def test_update_existing_item_success(self):
        """Обновление существующего элемента успешно"""
        # Подготовка
        update_data = {
            "name": "Мука обновленная",
            "full_name": "Пшеничная мука высший сорт"
        }
        
        # Действие
        result = self.service.update(Repository.nomenclature_key, "nomenclature-1", update_data)
        
        # Проверка
        self.assertTrue(result)
        updated_item = self.mock_repository_data[Repository.nomenclature_key]["nomenclature-1"]
        self.assertEqual(updated_item.name, "Мука обновленная")
        self.assertEqual(updated_item.full_name, "Пшеничная мука высший сорт")
    
    def test_update_partial_data_success(self):
        """Частичное обновление элемента успешно (PATCH семантика)"""
        # Подготовка
        update_data = {
            "name": "Мука новая"
        }
        
        # Действие
        result = self.service.update(Repository.nomenclature_key, "nomenclature-1", update_data)
        
        # Проверка
        self.assertTrue(result)
        updated_item = self.mock_repository_data[Repository.nomenclature_key]["nomenclature-1"]
        self.assertEqual(updated_item.name, "Мука новая")
        # Поле full_name не должно измениться
        self.assertEqual(updated_item.full_name, "Пшеничная мука")
    
    def test_update_nonexistent_item_returns_false(self):
        """Обновление несуществующего элемента возвращает False"""
        # Подготовка
        update_data = {"name": "Новое имя"}
        
        # Действие
        result = self.service.update(Repository.nomenclature_key, "nonexistent-id", update_data)
        
        # Проверка
        self.assertFalse(result)
    
    def test_update_with_dependencies_success(self):
        """Обновление элемента с зависимостями успешно"""
        # Подготовка
        new_group = GroupNomenclatureModel()
        new_group.id = "group-2"
        new_group.name = "Новая группа"
        self.mock_repository_data[Repository.group_nomenclature_key][new_group.id] = new_group
        
        update_data = {
            "group_nomenclature_id": "group-2"
        }
        
        # Действие
        result = self.service.update(Repository.nomenclature_key, "nomenclature-1", update_data)
        
        # Проверка
        self.assertTrue(result)
        updated_item = self.mock_repository_data[Repository.nomenclature_key]["nomenclature-1"]
        self.assertEqual(updated_item.group_nomenclature.id, "group-2")
    
    
    def test_delete_existing_item_success(self):
        """Удаление существующего элемента без зависимостей успешно"""
        # Подготовка - создаем элемент для удаления
        item_to_delete = GroupNomenclatureModel()
        item_to_delete.id = "to-delete"
        item_to_delete.name = "Для удаления"
        self.mock_repository_data[Repository.group_nomenclature_key][item_to_delete.id] = item_to_delete
        
        # Действие
        result = self.service.delete(Repository.group_nomenclature_key, "to-delete")
        
        # Проверка
        self.assertTrue(result)
        self.assertNotIn("to-delete", self.mock_repository_data[Repository.group_nomenclature_key])
    
    def test_delete_nonexistent_item_returns_false(self):
        """Удаление несуществующего элемента возвращает False"""
        # Действие
        result = self.service.delete(Repository.group_nomenclature_key, "nonexistent-id")
        
        # Проверка
        self.assertFalse(result)
    
    def test_delete_item_with_dependencies_raises_exception(self):
        """Удаление элемента с зависимостями вызывает исключение"""
        # Подготовка - создаем зависимость
        # Создаем рецепт с ингредиентом
        recipe = RecipeModel("Печенье", "Вкусное печенье")
        recipe.id = "recipe-1"
        
        ingredient = IngredientModel("Мука для печенья", self.nomenclature, 100)
        recipe.ingredients = [ingredient]
        
        self.mock_repository_data[Repository.recipe_key][recipe.id] = recipe
        
        # Проверка
        with self.assertRaises(OperationException):
            self.service.delete(Repository.nomenclature_key, "nomenclature-1")
    
    
    def test_create_item_from_data_nomenclature_success(self):
        """Создание номенклатуры из данных JSON успешно"""
        # Подготовка
        data = {
            "name": "Сахар",
            "full_name": "Сахарный песок",
            "group_nomenclature_id": "group-1",
            "unit_measurement_id": "unit-1"
        }
        
        # Действие
        result = self.service.create_item_from_data(Repository.nomenclature_key, data)
        
        # Проверка
        self.assertIsInstance(result, NomenclatureModel)
        self.assertEqual(result.name, "Сахар")
        self.assertEqual(result.full_name, "Сахарный песок")
        self.assertEqual(result.group_nomenclature.id, "group-1")
        self.assertEqual(result.unit_measurement.id, "unit-1")
        # ID должен быть сгенерирован автоматически
        self.assertIsNotNone(result.id)
    
    def test_create_item_from_data_with_custom_id_success(self):
        """Создание элемента с кастомным ID успешно"""
        # Подготовка
        data = {
            "id": "custom-id-123",
            "name": "Соль",
            "full_name": "Соль поваренная",
            "group_nomenclature_id": "group-1",
            "unit_measurement_id": "unit-1"
        }
        
        # Действие
        result = self.service.create_item_from_data(Repository.nomenclature_key, data)
        
        # Проверка
        self.assertEqual(result.id, "custom-id-123")
    
    def test_create_item_from_data_unit_measurement_success(self):
        """Создание единицы измерения из данных JSON успешно"""
        # Подготовка
        data = {
            "name": "Килограмм",
            "coefficient": 1000,
            "base_unit_id": "unit-1"
        }
        
        # Действие
        result = self.service.create_item_from_data(Repository.unit_measure_key, data)
        
        # Проверка
        self.assertIsInstance(result, UnitMeasurement)
        self.assertEqual(result.name, "Килограмм")
        self.assertEqual(result.coefficient, 1000)
        self.assertEqual(result.base_unit.id, "unit-1")
    
    def test_create_item_from_data_group_nomenclature_success(self):
        """Создание группы номенклатур из данных JSON успешно"""
        # Подготовка
        data = {
            "name": "Пряности"
        }
        
        # Действие
        result = self.service.create_item_from_data(Repository.group_nomenclature_key, data)
        
        # Проверка
        self.assertIsInstance(result, GroupNomenclatureModel)
        self.assertEqual(result.name, "Пряности")
    
    def test_create_item_from_data_storage_success(self):
        """Создание склада из данных JSON успешно"""
        # Подготовка
        data = {
            "name": "Дополнительный склад",
            "address": "ул. Пушкина 10"
        }
        
        # Действие
        result = self.service.create_item_from_data(Repository.storage_key, data)
        
        # Проверка
        self.assertIsInstance(result, StorageModel)
        self.assertEqual(result.name, "Дополнительный склад")
        self.assertEqual(result.address, "ул. Пушкина 10")
    
    def test_create_item_from_data_invalid_reference_type_raises_exception(self):
        """Создание элемента с неверным типом справочника вызывает исключение"""
        # Подготовка
        data = {"name": "Тест"}
        
        # Проверка
        with self.assertRaises(ArgumentException):
            self.service.create_item_from_data("invalid_type", data)
    
    
    def test_get_dependency_existing_success(self):
        """Получение существующей зависимости успешно"""
        # Действие
        result = self.service._get_dependency(Repository.group_nomenclature_key, "group-1")
        
        # Проверка
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "group-1")
    
    def test_get_dependency_nonexistent_raises_exception(self):
        """Получение несуществующей зависимости вызывает исключение"""
        # Проверка
        with self.assertRaises(ArgumentException):
            self.service._get_dependency(Repository.group_nomenclature_key, "nonexistent-dep")
    
    def test_get_dependency_empty_id_returns_none(self):
        """Получение зависимости с пустым ID возвращает None"""
        # Действие
        result = self.service._get_dependency(Repository.group_nomenclature_key, "")
        
        # Проверка
        self.assertIsNone(result)
    
    
    @patch('src.core.observe_service.ObserveService.create_event')
    def test_add_triggers_change_event(self, mock_create_event):
        """Добавление элемента вызывает событие изменения"""
        # Подготовка
        new_item = GroupNomenclatureModel()
        new_item.id = "new-item"
        new_item.name = "Новый элемент"
        
        # Действие
        self.service.add(Repository.group_nomenclature_key, new_item)
        
        # Проверка
        mock_create_event.assert_called_with(EventType.change_reference_type_key(), None)
    
    @patch('src.core.observe_service.ObserveService.create_event')
    def test_update_triggers_change_event(self, mock_create_event):
        """Обновление элемента вызывает событие изменения"""
        # Подготовка
        update_data = {"name": "Обновленное имя"}
        
        # Действие
        self.service.update(Repository.nomenclature_key, "nomenclature-1", update_data)
        
        # Проверка
        mock_create_event.assert_called_with(EventType.change_reference_type_key(), None)
    
    @patch('src.core.observe_service.ObserveService.create_event')
    def test_delete_triggers_events(self, mock_create_event):
        """Удаление элемента вызывает события"""
        # Подготовка - создаем элемент без зависимостей
        item_to_delete = GroupNomenclatureModel()
        item_to_delete.id = "to-delete"
        item_to_delete.name = "Для удаления"
        self.mock_repository_data[Repository.group_nomenclature_key][item_to_delete.id] = item_to_delete
        
        # Действие
        self.service.delete(Repository.group_nomenclature_key, "to-delete")
        
        # Проверка
        # Должно быть вызвано 2 события: delete и change
        self.assertEqual(mock_create_event.call_count, 2)
        
        # Первый вызов - событие удаления
        first_call_args = mock_create_event.call_args_list[0]
        self.assertEqual(first_call_args[0][0], EventType.delete_reference_type_key())
        
        # Второй вызов - событие изменения
        second_call_args = mock_create_event.call_args_list[1]
        self.assertEqual(second_call_args[0][0], EventType.change_reference_type_key())
    
    
    def test_check_nomenclature_dependencies_with_recipe(self):
        """Проверка зависимостей номенклатуры, используемой в рецепте"""
        # Подготовка - создаем рецепт с ингредиентом
        recipe = RecipeModel("Торт", "Вкусный торт")
        recipe.id = "recipe-1"
        
        ingredient = IngredientModel("Мука для торта", self.nomenclature, 200)
        recipe.ingredients = [ingredient]
        
        self.mock_repository_data[Repository.recipe_key][recipe.id] = recipe
        
        # Мокаем фабрику для проверки зависимостей
        with patch.object(self.service._ReferenceService__factory, 'check_dependencies') as mock_check:
            mock_check.return_value = ["Невозможно удалить номенклатуру. Она используется в рецепте 'Торт'"]
            
            # Проверка
            with self.assertRaises(OperationException) as context:
                self.service.delete(Repository.nomenclature_key, "nomenclature-1")
            
            self.assertIn("рецепте 'Торт'", str(context.exception))
    
    def test_check_unit_dependencies_with_nomenclature(self):
        """Проверка зависимостей единицы измерения, используемой в номенклатуре"""
        # Мокаем фабрику для проверки зависимостей
        with patch.object(self.service._ReferenceService__factory, 'check_dependencies') as mock_check:
            mock_check.return_value = ["Невозможно удалить единицу измерения. Она используется в номенклатуре 'Мука'"]
            
            # Проверка
            with self.assertRaises(OperationException) as context:
                self.service.delete(Repository.unit_measure_key, "unit-1")
            
            self.assertIn("номенклатуре 'Мука'", str(context.exception))
    
    def test_check_storage_dependencies_with_transaction(self):
        """Проверка зависимостей склада, используемого в транзакции"""
        # Подготовка - создаем транзакцию
        transaction = TransactionModel(
            datetime.date(2024, 1, 1),
            self.nomenclature,
            self.storage,
            100.0,
            self.unit
        )
        transaction.id = "transaction-1"
        
        self.mock_repository_data[Repository.transaction_key][transaction.id] = transaction
        
        # Мокаем фабрику для проверки зависимостей
        with patch.object(self.service._ReferenceService__factory, 'check_dependencies') as mock_check:
            mock_check.return_value = ["Невозможно удалить склад. Он используется в транзакции от 2024-01-01"]
            
            # Проверка
            with self.assertRaises(OperationException) as context:
                self.service.delete(Repository.storage_key, "storage-1")
            
            self.assertIn("транзакции от 2024-01-01", str(context.exception))
    
    
    def test_full_crud_cycle_success(self):
        """Полный цикл CRUD операций успешен"""
        # 1. CREATE
        data = {
            "name": "Новый продукт",
            "full_name": "Новый продукт полное название",
            "group_nomenclature_id": "group-1",
            "unit_measurement_id": "unit-1"
        }
        
        new_item = self.service.create_item_from_data(Repository.nomenclature_key, data)
        item_id = self.service.add(Repository.nomenclature_key, new_item)
        
        # Проверка создания
        self.assertIsNotNone(item_id)
        created_item = self.service.get_by_id(Repository.nomenclature_key, item_id)
        self.assertEqual(created_item.name, "Новый продукт")
        
        # 2. UPDATE
        update_data = {
            "name": "Обновленный продукт",
            "full_name": "Обновленный продукт полное название"
        }
        
        update_result = self.service.update(Repository.nomenclature_key, item_id, update_data)
        self.assertTrue(update_result)
        
        updated_item = self.service.get_by_id(Repository.nomenclature_key, item_id)
        self.assertEqual(updated_item.name, "Обновленный продукт")
        self.assertEqual(updated_item.full_name, "Обновленный продукт полное название")
        
        # 3. DELETE (если нет зависимостей)
        # Создаем еще один элемент для удаления (чтобы не трогать основной)
        data2 = {
            "name": "Для удаления",
            "full_name": "Элемент для удаления",
            "group_nomenclature_id": "group-1",
            "unit_measurement_id": "unit-1"
        }
        
        item_to_delete = self.service.create_item_from_data(Repository.nomenclature_key, data2)
        delete_item_id = self.service.add(Repository.nomenclature_key, item_to_delete)
        
        delete_result = self.service.delete(Repository.nomenclature_key, delete_item_id)
        self.assertTrue(delete_result)
        
        # Проверка удаления
        deleted_item = self.service.get_by_id(Repository.nomenclature_key, delete_item_id)
        self.assertIsNone(deleted_item)
    
    def test_reference_integrity_maintained(self):
        """Целостность ссылок между объектами сохраняется"""
        # Подготовка - создаем связанные объекты
        new_group = GroupNomenclatureModel()
        new_group.id = "new-group"
        new_group.name = "Новая группа"
        self.mock_repository_data[Repository.group_nomenclature_key][new_group.id] = new_group
        
        new_unit = UnitMeasurement("кг", 1000, self.unit)
        new_unit.id = "new-unit"
        self.mock_repository_data[Repository.unit_measure_key][new_unit.id] = new_unit
        
        # Создаем номенклатуру с зависимостями
        data = {
            "name": "Связанный продукт",
            "full_name": "Продукт со связями",
            "group_nomenclature_id": "new-group",
            "unit_measurement_id": "new-unit"
        }
        
        new_item = self.service.create_item_from_data(Repository.nomenclature_key, data)
        item_id = self.service.add(Repository.nomenclature_key, new_item)
        
        # Проверяем ссылки
        created_item = self.service.get_by_id(Repository.nomenclature_key, item_id)
        self.assertEqual(created_item.group_nomenclature.id, "new-group")
        self.assertEqual(created_item.unit_measurement.id, "new-unit")
        
        # Обновляем зависимости
        update_data = {
            "group_nomenclature_id": "group-1",  # Меняем на другую группу
            "unit_measurement_id": "unit-1"      # Меняем на другую единицу
        }
        
        self.service.update(Repository.nomenclature_key, item_id, update_data)
        
        updated_item = self.service.get_by_id(Repository.nomenclature_key, item_id)
        self.assertEqual(updated_item.group_nomenclature.id, "group-1")
        self.assertEqual(updated_item.unit_measurement.id, "unit-1")


if __name__ == '__main__':
    unittest.main()