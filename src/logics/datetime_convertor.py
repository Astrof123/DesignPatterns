from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common
from datetime import datetime


class DatetimeConvertor(AbstractConvertor):
    """
    Конвертор для datetime объектов.
    Преобразует datetime в строки стандартного формата.
    """

    def convert(self, obj) -> dict:
        """
        Конвертирует datetime поля в строки формата "ГГГГ-ММ-ДД ЧЧ:ММ:СС".
        
        Args:
            obj: Объект для конвертации
            
        Returns:
            dict: Словарь с отформатированными datetime полями
        """
        fields = common.get_fields(obj)
        result = {}

        for field in fields:
            value = getattr(obj, field)

            # Обрабатываем одиночные datetime объекты
            if isinstance(value, datetime):
                # Форматируем datetime в строку
                result[field] = value.strftime("%Y-%m-%d %H:%M:%S")

            # Обрабатываем списки datetime объектов
            if isinstance(value, list):
                if len(value) > 0:
                    # Проверяем, что список содержит datetime объекты
                    if isinstance(value[0], datetime):
                        value_new_list = []

                        # Рекурсивно обрабатываем каждый элемент списка
                        for v in value:
                            value_new_list.append(self.convert(v))

                        result[field] = value_new_list

        return result