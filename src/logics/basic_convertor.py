from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common

class BasicConvertor(AbstractConvertor):

    def convert(self, obj) -> dict:
        fields=common.get_fields(obj)
        result = {}

        for field in fields:
            value = getattr(obj, field)

            if isinstance(value, (int, float, str, bool)):
                result[field] = value

            if isinstance(value, list):
                if len(value) > 0:
                    if isinstance(value[0], (int, float, str, bool)):
                        value_new_list = []

                        for v in value:
                            value_new_list.append(self.convert(v))

                        result[field] = value_new_list

        return result