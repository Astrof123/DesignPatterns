import datetime
from src.core.validator import Validator
from src.models.unit_measurement_model import UnitMeasurement
from src.models.storage_model import StorageModel
from src.models.nomenclature_model import NomenclatureModel
from src.core.abstract_model import AbstractModel


class TransactionModel(AbstractModel):
    __date: datetime
    __nomenclature: NomenclatureModel
    __storage: StorageModel
    __quantity: float
    __unit: UnitMeasurement


    def __init__(self, date, nomenclature, storage, quantity, unit):
        super().__init__()
        self.date = date
        self.nomenclature = nomenclature
        self.storage = storage
        self.quantity = quantity
        self.unit = unit


    @property
    def date(self) -> datetime.date:
        return self.__date
    
    @date.setter
    def date(self, value: datetime.date):
        Validator.validate(value, datetime.date)
        self.__date = value


    @property
    def nomenclature(self) -> datetime:
        return self.__nomenclature
    
    @nomenclature.setter
    def nomenclature(self, value: NomenclatureModel):
        Validator.validate_models(value, NomenclatureModel)
        self.__nomenclature = value


    @property
    def storage(self) -> datetime:
        return self.__storage
    
    @storage.setter
    def storage(self, value: StorageModel):
        Validator.validate_models(value, StorageModel)
        self.__storage = value


    @property
    def quantity(self) -> datetime:
        return self.__quantity
    
    @quantity.setter
    def quantity(self, value: float):
        Validator.validate(value, float)
        self.__quantity = value


    @property
    def unit(self) -> datetime:
        return self.__unit
    
    @unit.setter
    def unit(self, value: UnitMeasurement):
        Validator.validate_models(value, UnitMeasurement)
        self.__unit = value
