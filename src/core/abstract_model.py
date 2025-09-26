from abc import ABC
import uuid

class AbstractModel(ABC):
    __id: str = ""


    def __init__(self):
        super().__init__()
        self.__id: str = uuid.uuid4()


    @property
    def id(self) -> str:
        return self.__id
    

    @id.setter
    def id(self, value: str) -> str:

        if isinstance(value, str):
            if value.strip() != "":
                self.__id = value.strip()
            else:
                raise ValueError("Поле id не должно быть пустым")
        else:
            raise ValueError("Поле id должно быть строкой")
        

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, AbstractModel):
            return False

        return self.__id == value.id