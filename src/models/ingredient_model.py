from src.core.validator import Validator
from src.models.nomenclature_model import NomenclatureModel
from src.core.entity_model import EntityModel


class IngredientModel(EntityModel):
    __count: int = 0
    __nomenclature: NomenclatureModel = None


    def __init__(self, name, nomenclature, count):
        super().__init__()
        self.name = name
        self.nomenclature = nomenclature
        self.count = count

    
    @property
    def count(self) -> int:
        return self.__count
    
    @count.setter
    def count(self, value: int) -> int:
        Validator.validate(value, int)
        self.__count = value


    @property
    def nomenclature(self) -> int:
        return self.__nomenclature
    
    @nomenclature.setter
    def nomenclature(self, value: NomenclatureModel) -> int:
        Validator.validate(value, NomenclatureModel)
        self.__nomenclature = value