from src.core.reference_item_factory import ReferenceItemFactory
from src.core.validator import Validator
from src.models.nomenclature_model import NomenclatureModel
from src.repository import Repository


class NomenclatureFactory(ReferenceItemFactory):
    """Фабрика для создания номенклатур"""
    
    def __init__(self, reference_service):
        self.reference_service = reference_service
    
    def create(self, data: dict) -> NomenclatureModel:
        """Создает новую номенклатуру"""
        Validator.validate(data.get('name'), str, field_name="name")
        
        # Получаем зависимости
        group = self.reference_service._get_dependency(
            Repository.group_nomenclature_key, 
            data.get('group_nomenclature_id')
        )
        unit = self.reference_service._get_dependency(
            Repository.unit_measure_key, 
            data.get('unit_measurement_id')
        )
        
        item = NomenclatureModel(
            name=data['name'],
            fullname=data.get('full_name', data['name']),
            group=group,
            unit=unit
        )
        
        # Устанавливаем кастомный ID если передан
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def update(self, existing_item: NomenclatureModel, update_data: dict):
        """Обновляет номенклатуру напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']
        
        if 'full_name' in update_data:
            existing_item.full_name = update_data['full_name']
        
        # Обновляем зависимости если переданы
        if 'group_nomenclature_id' in update_data:
            group = self.reference_service._get_dependency(
                Repository.group_nomenclature_key, 
                update_data['group_nomenclature_id']
            )
            existing_item.group_nomenclature = group
        
        if 'unit_measurement_id' in update_data:
            unit = self.reference_service._get_dependency(
                Repository.unit_measure_key, 
                update_data['unit_measurement_id']
            )
            existing_item.unit_measurement = unit


    def check_dependencies(self, nomenclature_id: str, reference_service) -> list:
        """Проверяет использование номенклатуры в других объектах"""
        errors = []
        
        # Проверка в рецептах
        recipes = reference_service._get_reference_data(Repository.recipe_key).values()
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                if ingredient.nomenclature.id == nomenclature_id:
                    errors.append(f"Невозможно удалить номенклатуру. Она используется в рецепте '{recipe.name}'")
                    break
            if errors:
                break
        
        # Проверка в транзакциях
        if not errors:  # Проверяем дальше только если нет ошибок
            transactions = reference_service._get_reference_data(Repository.transaction_key).values()
            for transaction in transactions:
                if transaction.nomenclature.id == nomenclature_id:
                    errors.append(f"Невозможно удалить номенклатуру. Она используется в транзакции от {transaction.date}")
                    break
        
        return errors