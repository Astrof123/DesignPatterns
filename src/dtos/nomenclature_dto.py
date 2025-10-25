from src.core.abstract_dto import AbstractDto

# Модель номенклатуры (dto)
# Пример
#                "name":"Пшеничная мука",
#                "range_id":"a33dd457-36a8-4de6-b5f1-40afa6193346",
#                "category_id":"7f4ecdab-0f01-4216-8b72-4c91d22b8918",
#                "id":"0c101a7e-5934-4155-83a6-d2c388fcc11a"

class NomenclatureDto(AbstractDto):
    __unit_measure_id:str = ""
    __group_nomenclature_id:str = ""


    @property
    def unit_measure_id(self) -> str:
        return self.__unit_measure_id

    @unit_measure_id.setter
    def unit_measure_id(self, value):
        self.__unit_measure_id = value

    @property
    def group_nomenclature_id(self) -> str:
        return self.__group_nomenclature_id

    @group_nomenclature_id.setter
    def group_nomenclature_id(self, value):
        self.__group_nomenclature_id = value
