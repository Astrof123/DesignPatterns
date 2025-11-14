from src.core.validator import Validator
from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common

class BasicConvertor(AbstractConvertor):
    """
    Конвертор для базовых типов данных.
    Обрабатывает примитивные типы
    """

    def convert(self, obj):
        Validator.validate(obj, (int, float, str, bool))
        return obj