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
        """
        Конвертирует ссылочные поля объектов в их ID.
        
        Args:
            obj: Объект для конвертации
            
        Returns:
            dict: Словарь с ID ссылочных полей
        """
        fields = common.get_fields(obj)
        result = {}

        for field in fields:
            value = getattr(obj, field)

            # Обрабатываем одиночные объекты моделей
            if isinstance(value, AbstractModel):
                # Заменяем объект на его идентификатор
                result[field] = value.id

            # Обрабатываем списки объектов моделей
            if isinstance(value, list):
                if len(value) > 0:
                    # Проверяем, что список содержит объекты моделей
                    if isinstance(value[0], AbstractModel):
                        value_new_list = []

                        # Для каждого объекта в списке берем его ID
                        for v in value:
                            value_new_list.append(v.id)

                        result[field] = value_new_list

        return result