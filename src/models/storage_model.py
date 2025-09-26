

from src.core.abstract_model import AbstractModel

class StorageModel(AbstractModel):
    __name: str = ""


    @property
    def name(self) -> str:
        return self.__name
    

    @name.setter
    def name(self, value: str) -> str:

        if isinstance(value, str):
            if value.strip() != "":
                self.__name = value.strip()
            else:
                raise ValueError("Поле name не должно быть пустым")
        else:
            raise ValueError("Поле name должно быть строкой")
        


        

