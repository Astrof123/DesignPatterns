from src.core.reference_item_factory import ReferenceItemFactory
from src.core.validator import Validator
from src.models.storage_model import StorageModel
from src.repository import Repository

class StorageFactory(ReferenceItemFactory):
    """Фабрика для создания складов"""
    
    def __init__(self, reference_service):
        self.reference_service = reference_service
    
    def create(self, data: dict) -> StorageModel:
        """Создает новый склад"""
        Validator.validate(data.get('name'), str, field_name="name")
        Validator.validate(data.get('address'), str, field_name="address")
        
        item = StorageModel(
            name=data['name'],
            address=data['address']
        )
        
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def update(self, existing_item: StorageModel, update_data: dict):
        """Обновляет склад напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']
        
        if 'address' in update_data:
            existing_item.address = update_data['address']


    def check_dependencies(self, storage_id: str, reference_service) -> list:
        """Проверяет использование склада в других объектах"""
        errors = []
        
        # Проверка в транзакциях
        transactions = reference_service._get_reference_data(Repository.transaction_key).values()
        for transaction in transactions:
            if transaction.storage.id == storage_id:
                errors.append(f"Невозможно удалить склад. Он используется в транзакции от {transaction.date}")
                break
        
        return errors