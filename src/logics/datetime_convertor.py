from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common
from datetime import datetime


class DatetimeConvertor(AbstractConvertor):

    def convert(self, obj) -> dict:
        fields=common.get_fields(obj)
        result = {}

        for field in fields:
            value = getattr(obj, field)

            if isinstance(value, datetime):
                result[field] = value.strftime("%Y-%m-%d %H:%M:%S")

            if isinstance(value, list):
                if len(value) > 0:
                    if isinstance(value[0], datetime):
                        value_new_list = []

                        for v in value:
                            value_new_list.append(self.convert(v))

                        result[field] = value_new_list


        return result