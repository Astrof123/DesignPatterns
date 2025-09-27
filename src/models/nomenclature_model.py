from src.models.unit_measurement_model import UnitMeasurement
from src.models.group_nomenclature_model import GroupNomenclature
from src.core.validator import Validator
from src.core.abstract_model import AbstractModel


class Nomenclature(AbstractModel):
    __full_name: str = ""
    __group_nomenclature: GroupNomenclature = None
    __unit_measurement: UnitMeasurement = None

    @property
    def full_name(self) -> str:
        return self.__full_name
    
    @full_name.setter
    def full_name(self, value: str) -> str:
        Validator.validate(value, str, 255, ">")
        self.__full_name = value

    
    @property
    def group_nomenclature(self):
        return self.__group_nomenclature

    @group_nomenclature.setter
    def group_nomenclature(self, value: GroupNomenclature):
        Validator.validate(value, GroupNomenclature)
        self.__group_nomenclature = value        


    @property
    def unit_measurement(self):
        return self.__unit_measurement
    
    @unit_measurement.setter
    def unit_measurement(self, value: UnitMeasurement):
        Validator.validate(value, UnitMeasurement)
        self.__unit_measurement = value           
