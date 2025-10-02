from src.core.validator import Validator
from src.core.abstract_model import AbstractModel


class UnitMeasurement(AbstractModel):
    __coefficient: int = 0
    __base_unit = None
    
    def __init__(self, name: str, coefficient: int, base_unit = None):
        super().__init__()
        
        self.name = name
        self.coefficient = coefficient
        self.base_unit = base_unit


    @property
    def coefficient(self) -> int:
        return self.__coefficient
    

    @coefficient.setter
    def coefficient(self, value: int):
        Validator.validate(value, int)
        self.__coefficient = value

    
    @property
    def base_unit(self):
        return self.__base_unit
    

    @base_unit.setter
    def base_unit(self, value):
        Validator.validate(value, (type(None), UnitMeasurement))
        self.__base_unit = value