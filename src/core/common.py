from src.core.entity_model import EntityModel
from src.core.abstract_model import AbstractModel
from src.core.validator import ArgumentException

# Набор статических общих методов
class common:

    """
    Получить список наименований всех моделей
    """
    @staticmethod
    def get_models() -> list:
        result = []
        for inheritor in EntityModel.__subclasses__():
            result.append(inheritor.__name__)

        return result    


    """
    Получить полный список полей любой модели
        - is_common = True - исключить из списка словари и списки
        - prefix: префикс для вложенных полей
    """
    @staticmethod
    def get_fields(source, is_common: bool = False, prefix = "") -> list:
        if source is None:
            raise ArgumentException("Некорректно переданы аргументы!")

        items = list(filter(lambda x: not x.startswith("_") , dir(source))) 
        result = []

        for item in items:
            attribute = getattr(source.__class__, item)
            if isinstance(attribute, property):
                value = getattr(source, item)

                # Флаг. Только простые типы и модели включать
                if is_common == True and (isinstance(value, dict) or isinstance(value, list) ):
                    continue

                result.append(prefix + item)

        return result
    

    """
    Получить список полей включая вложенные объекты
    Рекурсивно обходит внутренние объекты-модели
    """
    @staticmethod
    def get_fields_including_internal(source, is_common: bool = False) -> list:
        if source is None:
            raise ArgumentException("Некорректно переданы аргументы!")

        items = list(filter(lambda x: not x.startswith("_") , dir(source))) 
        result = []

        for item in items:
            attribute = getattr(source.__class__, item)
            if isinstance(attribute, property):
                value = getattr(source, item)

                if is_common == True and (isinstance(value, dict) or isinstance(value, list) ):
                    continue

                if isinstance(value, AbstractModel):
                    inner_result = common.get_fields(value, False, f"{item}/")
                    result.extend(inner_result)
                else:
                    result.append(item)

        return result