from src.core.abstract_model import AbstractModel
from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common
from datetime import datetime


class ReferenceConvertor(AbstractConvertor):

    def convert(self, obj) -> dict:
        fields=common.get_fields(obj)
        result = {}

        for field in fields:
            value = getattr(obj, field)

            if isinstance(value, AbstractModel):
                result[field] = value.id

            if isinstance(value, list):
                if len(value) > 0:
                    if isinstance(value[0], AbstractModel):
                        value_new_list = []

                        for v in value:
                            value_new_list.append(v.id)

                        result[field] = value_new_list

        return result