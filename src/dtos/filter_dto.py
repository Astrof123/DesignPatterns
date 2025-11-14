from src.core.abstract_dto import AbstractDto


class FilterDto(AbstractDto):
    __field_name: str = ""
    __value: str = ""
    
    @property
    def field_name(self) -> str:
        return self.__field_name
    
    @field_name.setter
    def field_name(self, value: str):
        self.__field_name = value

    @property
    def value(self) -> str:
        return self.__value
    
    @value.setter
    def value(self, value: str):
        self.__value = value

    