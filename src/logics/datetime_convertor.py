from src.core.validator import Validator
from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common
from datetime import datetime


class DatetimeConvertor(AbstractConvertor):
    """
    Конвертор для datetime объектов.
    Преобразует datetime в строки стандартного формата.
    """

    def convert(self, obj) -> dict:
        Validator.validate(obj, datetime)
        return obj.strftime("%Y-%m-%d %H:%M:%S")