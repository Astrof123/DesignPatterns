

from src.core.validator import Validator
from src.core.entity_model import EntityModel

class StorageModel(EntityModel):
    __address: str = ""

    def __init__(self, name, address):
        super().__init__()
        self.name = name
        self.address = address
        
    @property
    def address(self) -> str:
        return self.__address
    
    @address.setter
    def address(self, value: str) -> str:
        Validator.validate(value, str, 255, ">")
        self.__address = value

        

