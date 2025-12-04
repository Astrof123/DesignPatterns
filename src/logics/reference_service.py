from src.logics.reference_factory import ReferenceFactory
from src.core.event_type import EventType
from src.core.observe_service import ObserveService
from src.core.validator import Validator, ArgumentException

from src.repository import Repository

class ReferenceService:
    """Сервис для работы со справочниками"""
    
    def __init__(self, repository_data: dict):
        Validator.validate(repository_data, dict)
        self.__data = repository_data
        self.__factory = ReferenceFactory(self) 
    
    @property
    def data(self):
        return self.__data
    
    def _get_reference_data(self, reference_type: str) -> dict:
        """Получить данные справочника по типу"""
        if reference_type not in Repository.get_key_fields(Repository):
            raise ArgumentException(f"Неверный тип справочника: {reference_type}")
        
        return self.data.get(reference_type, {})
    
    def _set_reference_data(self, reference_type: str, data: dict):
        """Установить данные справочника"""
        if reference_type not in Repository.get_key_fields(Repository):
            raise ArgumentException(f"Неверный тип справочника: {reference_type}")
        
        self.data[reference_type] = data
    
    def get_by_id(self, reference_type: str, id: str):
        """Получить элемент справочника по ID"""
        data_dict = self._get_reference_data(reference_type)
        return data_dict.get(id)
    
    def add(self, reference_type: str, item) -> str:
        """Добавить новый элемент в справочник"""
        Validator.validate(item, object)
        
        data_dict = self._get_reference_data(reference_type)
        
        # Проверяем уникальность ID
        for key, existing_item in data_dict.items():
            if existing_item.id == item.id:
                raise ArgumentException(f"Элемент с ID {item.id} уже существует")

        data_dict[item.id] = item
        self._set_reference_data(reference_type, data_dict)
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)

        return item.id
    
    def update(self, reference_type: str, id: str, update_data: dict) -> bool:
        """Обновить элемент справочника с обновлением зависимостей"""
        Validator.validate(id, str)
        Validator.validate(update_data, dict)
        
        data_dict = self._get_reference_data(reference_type)
        
        # Ищем существующий элемент
        existing_item = None
        for item in data_dict.values():
            if item.id == id:
                existing_item = item
                break

        if not existing_item:
            return False

        # Используем фабрику для обновления элемента
        self.__factory.update_item(reference_type, existing_item, update_data)
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)
        
        return True
    
    def delete(self, reference_type: str, id: str) -> bool:
        """Удалить элемент из справочника"""
        Validator.validate(id, str)
        
        # Проверяем наличие зависимостей перед удалением
        ObserveService.create_event(EventType.delete_reference_type_key(), {
            "reference_type": reference_type, 
            "item_id": id, 
            "reference_service": self
        })
        
        data_dict = self._get_reference_data(reference_type)
        
        # Ищем элемент для удаления
        item_to_delete = None
        for key, item in data_dict.items():
            if item.id == id:
                item_to_delete = key
                break

        if not item_to_delete:
            return False
        
        del data_dict[item_to_delete]
        self._set_reference_data(reference_type, data_dict)

        ObserveService.create_event(EventType.change_reference_type_key(), None)
        
        return True
    
    def create_item_from_data(self, reference_type: str, data: dict):
        """Создает новый элемент справочника из данных JSON"""
        # Используем фабрику для создания элемента
        return self.__factory.create_item(reference_type, data)
    
    
    def _get_dependency(self, reference_type: str, dependency_id: str):
        """Получает зависимый объект по ID"""
        if not dependency_id:
            return None
            
        dependency = self.get_by_id(reference_type, dependency_id)
        if not dependency:
            raise ArgumentException(f"Зависимость {reference_type} с ID {dependency_id} не найдена")
            
        return dependency