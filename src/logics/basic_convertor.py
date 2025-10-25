from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common

class BasicConvertor(AbstractConvertor):
    """
    Конвертор для базовых типов данных.
    Обрабатывает примитивные типы и их списки.
    """

    def convert(self, obj) -> dict:
        """
        Конвертирует объект, извлекая только базовые типы данных.
        
        Args:
            obj: Объект для конвертации
            
        Returns:
            dict: Словарь с базовыми полями объекта
        """
        # Получаем все поля объекта через утилиту common
        fields = common.get_fields(obj)
        result = {}

        for field in fields:
            value = getattr(obj, field)

            # Обрабатываем одиночные значения базовых типов
            if isinstance(value, (int, float, str, bool)):
                result[field] = value

            # Обрабатываем списки базовых типов
            if isinstance(value, list):
                if len(value) > 0:
                    # Проверяем, что список содержит базовые типы
                    if isinstance(value[0], (int, float, str, bool)):
                        value_new_list = []

                        # Рекурсивно обрабатываем каждый элемент списка
                        for v in value:
                            value_new_list.append(self.convert(v))

                        result[field] = value_new_list

        return result