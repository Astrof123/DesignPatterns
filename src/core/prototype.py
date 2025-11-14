from abc import ABC, abstractmethod
from src.core.validator import Validator
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
    def filter(data: list, filter: FilterDto):
        if len(data) == 0:
            return data
        
        first_item = data[0]

        result = []
        for field in common.get_fields(first_item):
            for item in data:
                if field == filter.field_name:
                    value = str(getattr(item, field))
                    if value == filter.value:
                        result.append(item)

        return result
