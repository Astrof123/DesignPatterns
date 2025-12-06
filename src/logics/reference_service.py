from src.logics.reference_factory import ReferenceFactory
from src.core.event_type import EventType
from src.core.observe_service import ObserveService
from src.core.validator import Validator, ArgumentException
from src.core.logger import Logger
from src.repository import Repository

class ReferenceService:
    """Сервис для работы со справочниками"""
    
    def __init__(self, repository_data: dict):
        Validator.validate(repository_data, dict)
        self.__data = repository_data
        self.__factory = ReferenceFactory(self)
        
        # Логируем создание сервиса
        Logger.debug("ReferenceService", "Сервис справочников создан")
    
    @property
    def data(self):
        return self.__data
    
    def _get_reference_data(self, reference_type: str) -> dict:
        """Получить данные справочника по типу"""
        if reference_type not in Repository.get_key_fields(Repository):
            error_msg = f"Неверный тип справочника: {reference_type}"
            Logger.error("ReferenceService", error_msg)
            raise ArgumentException(error_msg)
        
        Logger.debug("ReferenceService", f"Получены данные справочника: {reference_type}")
        return self.data.get(reference_type, {})
    
    def _set_reference_data(self, reference_type: str, data: dict):
        """Установить данные справочника"""
        if reference_type not in Repository.get_key_fields(Repository):
            error_msg = f"Неверный тип справочника: {reference_type}"
            Logger.error("ReferenceService", error_msg)
            raise ArgumentException(error_msg)
        
        self.data[reference_type] = data
        Logger.debug("ReferenceService", f"Обновлены данные справочника: {reference_type}")
    
    def get_by_id(self, reference_type: str, id: str):
        """Получить элемент справочника по ID"""
        Logger.debug("ReferenceService", f"Поиск элемента {id} в справочнике {reference_type}")
        data_dict = self._get_reference_data(reference_type)
        item = data_dict.get(id)
        
        if item:
            Logger.debug("ReferenceService", f"Элемент {id} найден")
        else:
            Logger.debug("ReferenceService", f"Элемент {id} не найден")
        
        return item
    
    def add(self, reference_type: str, item) -> str:
        """Добавить новый элемент в справочник"""
        Validator.validate(item, object)
        
        Logger.info("ReferenceService", f"Добавление элемента в справочник {reference_type}", 
                   {"item_id": getattr(item, 'id', 'unknown'), "item_type": type(item).__name__})
        
        data_dict = self._get_reference_data(reference_type)
        
        # Проверяем уникальность ID
        for key, existing_item in data_dict.items():
            if existing_item.id == item.id:
                error_msg = f"Элемент с ID {item.id} уже существует"
                Logger.error("ReferenceService", error_msg)
                raise ArgumentException(error_msg)

        data_dict[item.id] = item
        self._set_reference_data(reference_type, data_dict)
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)
        
        Logger.info("ReferenceService", f"Элемент успешно добавлен: {item.id}")
        return item.id
    
    def update(self, reference_type: str, id: str, update_data: dict) -> bool:
        """Обновить элемент справочника с обновлением зависимостей"""
        Validator.validate(id, str)
        Validator.validate(update_data, dict)
        
        Logger.info("ReferenceService", f"Обновление элемента {id} в справочнике {reference_type}", 
                   {"update_data": update_data})
        
        data_dict = self._get_reference_data(reference_type)
        
        # Ищем существующий элемент
        existing_item = None
        for item in data_dict.values():
            if item.id == id:
                existing_item = item
                break

        if not existing_item:
            Logger.warning("ReferenceService", f"Элемент {id} не найден для обновления")
            return False

        # Используем фабрику для обновления элемента
        self.__factory.update_item(reference_type, existing_item, update_data)
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)
        
        Logger.info("ReferenceService", f"Элемент {id} успешно обновлен")
        return True
    
    def delete(self, reference_type: str, id: str) -> bool:
        """Удалить элемент из справочника"""
        Validator.validate(id, str)
        
        Logger.info("ReferenceService", f"Удаление элемента {id} из справочника {reference_type}")
        
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
            Logger.warning("ReferenceService", f"Элемент {id} не найден для удаления")
            return False
        
        del data_dict[item_to_delete]
        self._set_reference_data(reference_type, data_dict)

        ObserveService.create_event(EventType.change_reference_type_key(), None)
        
        Logger.info("ReferenceService", f"Элемент {id} успешно удален")
        return True
    
    def create_item_from_data(self, reference_type: str, data: dict):
        """Создает новый элемент справочника из данных JSON"""
        Logger.debug("ReferenceService", f"Создание элемента из данных для {reference_type}", data)
        # Используем фабрику для создания элемента
        return self.__factory.create_item(reference_type, data)
    
    def _get_dependency(self, reference_type: str, dependency_id: str):
        """Получает зависимый объект по ID"""
        if not dependency_id:
            return None
            
        Logger.debug("ReferenceService", f"Поиск зависимости {dependency_id} в {reference_type}")
        dependency = self.get_by_id(reference_type, dependency_id)
        if not dependency:
            error_msg = f"Зависимость {reference_type} с ID {dependency_id} не найдена"
            Logger.error("ReferenceService", error_msg)
            raise ArgumentException(error_msg)
            
        return dependency