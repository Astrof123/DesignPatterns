from abc import ABC, abstractmethod
from src.core.common import common
from src.core.validator import Validator, OperationException


"""
Абстрактный класс для наследования только dto структур
"""
class AbstractDto(ABC):
    __name:str = ""
    __id:str = ""

    @property
    def name(self) ->str:
        return self.__name
    
    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value   

    # Универсальный фабричный метод для загрузщки dto из словаря
    @abstractmethod
    def create(self, data) -> "AbstractDto":
        Validator.validate(data, dict)
        fields = common.get_fields(self)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        try:
            for key in matching_keys:
                setattr(self, key, data[ key ])
        except:
            raise OperationException("Невозможно загрузить данные!")    

        return self