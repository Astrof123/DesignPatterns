from src.core.reference_item_factory import ReferenceItemFactory
from src.core.validator import Validator
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.repository import Repository

class GroupNomenclatureFactory(ReferenceItemFactory):
    """Фабрика для создания групп номенклатур"""
    
    def __init__(self, reference_service):
        self.reference_service = reference_service
    
    def create(self, data: dict) -> GroupNomenclatureModel:
        """Создает новую группу номенклатур"""
        Validator.validate(data.get('name'), str, field_name="name")
        
        item = GroupNomenclatureModel()
        item.name = data['name']
        
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def update(self, existing_item: GroupNomenclatureModel, update_data: dict):
        """Обновляет группу номенклатур напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']


    def check_dependencies(self, group_id: str, reference_service) -> list:
        """Проверяет использование группы номенклатур в других объектах"""
        errors = []
        
        # Проверка в номенклатурах
        nomenclatures = reference_service._get_reference_data(Repository.nomenclature_key).values()
        for nomenclature in nomenclatures:
            if nomenclature.group_nomenclature.id == group_id:
                errors.append(f"Невозможно удалить группу номенклатур. Она используется в номенклатуре '{nomenclature.name}'")
                break
        
        return errors