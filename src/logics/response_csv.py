from src.core.abstract_response import AbstractResponse
from src.core.common import common

class ResponseCsv(AbstractResponse):

    # Сформировать CSV 
    def create(self, format: str, data: list):
        text = super().create(format, data)

        # Шапка
        item = data[0]

        fields = common.get_fields(item)

        for field in fields:
            text += f"{field};"

        # Данные
        return text