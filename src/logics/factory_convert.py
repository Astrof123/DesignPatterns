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
        """
        Выполняет полную конвертацию объекта через все конверторы.
        Объединяет результаты в единый словарь.
        
        Args:
            obj: Объект для конвертации
            
        Returns:
            dict: Комбинированный словарь со всеми преобразованными полями
        """
        # Последовательно применяем все конверторы
        # BasicConvertor - базовые типы
        result = self.__match["basic"]().convert(obj)
        # DatetimeConvertor - datetime поля (объединяем с предыдущим результатом)
        result = result | self.__match["datetime"]().convert(obj)
        # ReferenceConvertor - ссылочные поля (объединяем с предыдущим результатом)
        result = result | self.__match["reference"]().convert(obj)
        
        return result