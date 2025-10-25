

from src.logics.reference_convertor import ReferenceConvertor
from src.logics.basic_convertor import BasicConvertor
from src.logics.datetime_convertor import DatetimeConvertor


class FactoryConvert:
    __match = {
        "basic": BasicConvertor,
        "datetime": DatetimeConvertor,
        "reference": ReferenceConvertor
    }

    def convert(self, obj) -> dict:
        result = self.__match["basic"]().convert(obj)
        result = result | self.__match["datetime"]().convert(obj)
        result = result | self.__match["reference"]().convert(obj)
        
        return result