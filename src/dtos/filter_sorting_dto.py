from src.dtos.filter_dto import FilterDto
from src.core.validator import Validator

class FilterSortingDto:
    """
    DTO для передачи параметров фильтрации и сортировки
    Используется в методах фильтрации Prototype
    """


    __filters = []
    __sorting = []

    @property
    def filters(self) -> list:
        return self.__filters


    def __init__(self, filters, sorting):
        Validator.validate(filters, list)
        Validator.validate(sorting, list)
        self.__filters = filters
        self.__sorting = sorting


    # Пример структуры
    # {
    #     "filters": [
    #         {
    #             "field_name": "name",
    #             "value": "Пшеничная мука",
    #             "type": "LIKE"
    #         },
    #         {
    #             "field_name": "base_unit/name",
    #             "value": "грамм",
    #             "type": "LIKE"
    #         },
    #         {
    #             "field_name": "name",
    #             "value": "кг",
    #             "type": "EQUALS"
    #         }
    #     ],
    #     "sorting": [
    #         "range_name"
    #     ]
    # }


