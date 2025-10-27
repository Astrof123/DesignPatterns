from abc import ABC, abstractmethod

class AbstractConvertor(ABC):
    """
    Абстрактный базовый класс для всех конверторов.
    Определяет интерфейс для преобразования объектов в словари.
    """
    
    @abstractmethod
    def convert(self, obj) -> dict:
        """
        Абстрактный метод для конвертации объекта в словарь.
        
        Args:
            obj: Любой объект для конвертации
            
        Returns:
            dict: Словарь с преобразованными данными
        """
        pass