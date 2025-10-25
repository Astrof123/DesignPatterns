from abc import ABC, abstractmethod

class AbstractConvertor(ABC):
    
    @abstractmethod
    def convert(self, obj) -> dict:
        pass

