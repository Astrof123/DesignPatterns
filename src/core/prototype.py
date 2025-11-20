from abc import ABC, abstractmethod
from src.core.filter_type import FilterType
from src.dtos.filter_sorting_dto import FilterSortingDto
from src.core.validator import ArgumentException, Validator
from src.dtos.filter_dto import FilterDto 
from src.core.common import common

# Абстрактный класс - прототип
class Prototype:
    __data: list = []

    # Набор данных
    @property
    def data(self):
        return self.__data

    def __init__(self, data: list):
        Validator.validate(data, list)
        self.__data = data


    # Клонирование
    def clone(self, data: list = None) -> "Prototype":
        inner_data = None

        if data is None:
            inner_data = self.__data
        else:
            inner_data = data

        instance = Prototype(inner_data)
        return instance
    
    # Универсальный фильтр
    @staticmethod
    def filter(source: "Prototype", filters: FilterSortingDto):
        """
        Универсальная фильтрация данных по набору фильтров
        Поддерживает вложенные поля через нотацию 'field/subfield'
        """

        if len(source.data) == 0:
            return source
        
        
        result = source.data[:]
        for filter in filters.filters:
            if len(result) == 0:
                break

            if filter["type"].lower() not in FilterType.get_all_types():
                raise ArgumentException("Не верно указан type в одном из фильтров")

            upper = None
            if "/" in filter["field_name"]:
                splitted = filter["field_name"].split("/")
                upper = splitted[0]
                nested = splitted[1]
                
                result = Prototype.filter_cycle_nested(result, nested, filter["type"], filter["value"], upper)
            else:
                result = Prototype.filter_cycle(result, filter["field_name"], filter["type"], filter["value"])


        return source.clone(result)

    @staticmethod
    def filter_cycle(data, filter_field_name, fitler_type, filter_value):
        """Цикл фильтрации для обычных полей"""

        first_item = data[0]

        result = []
        if hasattr(first_item, filter_field_name):
            for item in data:
                value = getattr(item, filter_field_name)
                    
                condition = False

                if fitler_type == FilterType.equals():
                    condition = value == filter_value

                elif fitler_type == FilterType.like():
                    condition = filter_value in value

                elif fitler_type == FilterType.less():
                    condition = value < filter_value

                elif fitler_type == FilterType.greater():
                    condition = value > filter_value

                elif fitler_type == FilterType.less_or_equal():
                    condition = value <= filter_value

                elif fitler_type == FilterType.greater_or_equal():
                    condition = value >= filter_value

                elif fitler_type == FilterType.not_equals():
                    condition = value != filter_value

                if condition:
                    result.append(item)

        else:
            raise ArgumentException("Не верно указан field_name в одном из фильтров")

        return result

    def filter_cycle_nested(data, filter_field_name, fitler_type, filter_value, upper_field_name):
        """Цикл фильтрации для вложенных полей"""

        check_item = getattr(data[0], upper_field_name)

        result = []
        if hasattr(check_item, filter_field_name):
            for item in data:
                upper_field = getattr(item, upper_field_name)
                value = getattr(upper_field, filter_field_name)
                    
                condition = False

                if fitler_type == FilterType.equals():
                    condition = value == filter_value

                elif fitler_type == FilterType.like():
                    condition = filter_value in value 

                elif fitler_type == FilterType.less():
                    condition = value > filter_value

                elif fitler_type == FilterType.greater():
                    condition = value < filter_value

                elif fitler_type == FilterType.less_or_equal():
                    condition = value >= filter_value

                elif fitler_type == FilterType.greater_or_equal():
                    condition = value <= filter_value

                elif fitler_type == FilterType.not_equals():
                    condition = value != filter_value

                if condition:
                    result.append(item)

        else:
            raise ArgumentException("Не верно указан field_name в одном из фильтров")

        return result
