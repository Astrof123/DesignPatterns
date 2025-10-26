from src.core.validator import Validator
from src.core.abstract_model import AbstractModel
from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common
from datetime import datetime


class ReferenceConvertor(AbstractConvertor):
    """
    Конвертор для ссылочных типов данных.
    Преобразует объекты моделей в их идентификаторы.
    """

    def convert(self, obj) -> dict:
        Validator.validate(obj, AbstractModel)
        return obj.id