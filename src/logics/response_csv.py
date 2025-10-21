from src.core.abstract_response import AbstractResponse
from src.core.common import common

class ResponseCsv(AbstractResponse):

    def __init__(self):
        super().__init__()

    # Преобразует данные в формат CSV
    def build(self, format: str, data: list):
        text = super().build(format, data)

        # Шапка
        item = data[0]
        fields = common.get_fields(item)

        # Шапка CSV
        for field in fields:
            text += f"{field};"
            
        text = text.rstrip(';') + "\n"

        # Данные
        for item in data:
            for field in fields:
                value = getattr(item, field, "")
                # Обрабатываем вложенные объекты
                if hasattr(value, 'name'):
                    text += f"{value.name};"
                elif hasattr(value, 'id'):
                    text += f"{value.id};"
                else:
                    text += f"{value};"
            text = text.rstrip(';') + "\n"
        
        return text