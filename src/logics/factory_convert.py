from datetime import datetime
from src.core.abstract_model import AbstractModel
from src.core.common import common
from src.logics.reference_convertor import ReferenceConvertor
from src.logics.basic_convertor import BasicConvertor
from src.logics.datetime_convertor import DatetimeConvertor


class FactoryConvert:
    """
    Фабрика для комбинированной конвертации объектов.
    Объединяет результаты работы всех специализированных конверторов.
    """

    # Словарь соответствия типов конверторов их классам
    __match = {
        "basic": BasicConvertor,      # Для базовых типов
        "datetime": DatetimeConvertor, # Для datetime полей
        "reference": ReferenceConvertor # Для ссылочных полей
    }

    def convert(self, obj) -> dict:

        fields = common.get_fields(obj)
        result = {}

        for field in fields:
            value = getattr(obj, field)

            if isinstance(value, (int, float, str, bool)):
                result[field] = self.__match["basic"]().convert(value)

            elif isinstance(value, AbstractModel):
                result[field] = self.__match["reference"]().convert(value)

            elif isinstance(value, datetime):
                result[field] = self.__match["datetime"]().convert(value)

            elif isinstance(value, list):
                result[field] = []
                for v in value:
                    result[field].append(self.convert(v))

        return result