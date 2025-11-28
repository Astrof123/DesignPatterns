from abc import ABC, abstractmethod
from src.core.event_type import EventType
import uuid

from src.core.validator import Validator, OperationException

class AbstractModel(ABC):
    __id: str = ""

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.__id: str = str(uuid.uuid4())


    @property
    def id(self) -> str:
        return self.__id
    

    @id.setter
    def id(self, value: str) -> str:
        Validator.validate(value, str)
        self.__id = value.strip()
                

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, AbstractModel):
            return False

        return self.__id == value.id
    
    """
    Обработка события
    """
    def handle(self, event: str, params):
        Validator.validate(event, str)
        events = EventType.events()

        if event not in events:
            raise OperationException(f"{events} - не является событием!")
        

    