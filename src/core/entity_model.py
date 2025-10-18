from src.core.abstract_model import AbstactModel
from src.core.validator import Validator


"""
Общий класс для наследования. Содержит стандартное определение: код, наименование
"""
class EntityModel(AbstactModel):
    __name:str = ""

    # Наименование
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value:str):
        Validator.validate(value, str)
        self.__name = value.strip()


    # Фабричный метод
    @staticmethod
    def create(name:str):
        item = EntityModel()
        item.name = name
        return item
    
  