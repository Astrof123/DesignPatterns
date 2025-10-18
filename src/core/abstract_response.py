from src.core.validator import Validator, OperationException
from abc import ABC, abstractmethod

# Абстрактный класс для формирования ответов
class AbstractResponse(ABC):
    
    # Сформировать нужный ответ
    @abstractmethod
    def build(self, format: str, data: list) -> str:
        Validator.validate(format, str)
        Validator.validate(data, list)

        if len(data) == 0:
            raise OperationException("Нет данных!")

        return f""