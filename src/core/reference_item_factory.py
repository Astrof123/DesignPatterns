from abc import ABC, abstractmethod

class ReferenceItemFactory(ABC):
    """Абстрактная фабрика для создания элементов справочников"""
    
    @abstractmethod
    def create(self, data: dict):
        """Создает новый элемент"""
        pass
    
    @abstractmethod
    def update(self, existing_item, update_data: dict):
        """Обновляет существующий элемент"""
        pass

    @abstractmethod
    def check_dependencies(self, item_id: str, reference_service) -> list:
        """Проверяет зависимости элемента"""
        pass