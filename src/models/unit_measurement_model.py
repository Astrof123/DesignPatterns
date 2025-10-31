from src.core.validator import Validator
from src.core.entity_model import EntityModel


class UnitMeasurement(EntityModel):
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

    """
    Возвращает корневую единицу измерения
    """
    def root_base_unit(self):
        if self.base_unit == None:
            return self
        else:
            return self.base_unit.root_base_unit()

    """
    Возвращает quantity приведенную к корневой единице измерения
    """
    def convert_to_root_base_unit(self, quantity):
        if self.base_unit == None:
            return quantity
        else:
            return self.base_unit.convert_to_root_base_unit(quantity * self.coefficient)

    '''
    Киллограмм
    '''
    @staticmethod
    def create_kilo(gramm):
        return UnitMeasurement.create("кг", 1000, gramm)


    '''
    Грамм
    '''
    @staticmethod
    def create_gramm():
        return UnitMeasurement.create("грамм", 1)

    '''
    Фабричный метод
    '''
    @staticmethod
    def create(name: str, coefficient: int, base_unit = None):
        Validator.validate(name, str)
        Validator.validate(coefficient, int)
        Validator.validate(base_unit, (type(None), UnitMeasurement))
        return UnitMeasurement(name, coefficient, base_unit)

        