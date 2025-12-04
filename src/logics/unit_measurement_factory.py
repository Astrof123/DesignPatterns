from src.core.reference_item_factory import ReferenceItemFactory
from src.core.validator import Validator
from src.models.unit_measurement_model import UnitMeasurement
from src.repository import Repository

class UnitMeasurementFactory(ReferenceItemFactory):
    """Фабрика для создания единиц измерения"""
    
    def __init__(self, reference_service):
        self.reference_service = reference_service
    
    def create(self, data: dict) -> UnitMeasurement:
        """Создает новую единицу измерения"""
        Validator.validate(data.get('name'), str, field_name="name")
        Validator.validate(data.get('coefficient'), int, field_name="coefficient")
        
        base_unit = None
        if data.get('base_unit_id'):
            base_unit = self.reference_service._get_dependency(
                Repository.unit_measure_key, 
                data['base_unit_id']
            )
        
        item = UnitMeasurement(
            name=data['name'],
            coefficient=data['coefficient'],
            base_unit=base_unit
        )
        
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def update(self, existing_item: UnitMeasurement, update_data: dict):
        """Обновляет единицу измерения напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']
        
        if 'coefficient' in update_data:
            existing_item.coefficient = update_data['coefficient']
        
        if 'base_unit_id' in update_data:
            base_unit = self.reference_service._get_dependency(
                Repository.unit_measure_key, 
                update_data['base_unit_id']
            ) if update_data['base_unit_id'] else None
            existing_item.base_unit = base_unit


    def check_dependencies(self, unit_id: str, reference_service) -> list:
        """Проверяет использование единицы измерения в других объектах"""
        errors = []
        
        # Проверка в номенклатурах
        nomenclatures = reference_service._get_reference_data(Repository.nomenclature_key).values()
        for nomenclature in nomenclatures:
            if nomenclature.unit_measurement.id == unit_id:
                errors.append(f"Невозможно удалить единицу измерения. Она используется в номенклатуре '{nomenclature.name}'")
                break
        
        # Проверка в транзакциях
        if not errors:
            transactions = reference_service._get_reference_data(Repository.transaction_key).values()
            for transaction in transactions:
                if transaction.unit.id == unit_id:
                    errors.append(f"Невозможно удалить единицу измерения. Она используется в транзакции от {transaction.date}")
                    break
        
        # Проверка в других единицах измерения (как базовая)
        if not errors:
            units = reference_service._get_reference_data(Repository.unit_measure_key).values()
            for unit in units:
                if unit.base_unit and unit.base_unit.id == unit_id:
                    errors.append(f"Невозможно удалить единицу измерения. Она используется как базовая для '{unit.name}'")
                    break
        
        return errors