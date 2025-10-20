from src.core.abstract_response import AbstractResponse
from src.core.common import common

class ResponseMarkdown(AbstractResponse):

    def __init__(self):
        super().__init__()

    def build(self, format: str, data: list):
        text = super().build(format, data)
 
        # Шапка таблицы
        item = data[0]
        fields = common.get_fields(item)
        
        # Заголовок таблицы
        text += "| " + " | ".join(fields) + " |\n"
        text += "| " + " | ".join(["---"] * len(fields)) + " |\n"
        
        # Данные
        for item in data:
            row = []
            for field in fields:
                value = getattr(item, field, "")
                # Обрабатываем вложенные объекты
                if hasattr(value, 'name'):
                    row.append(str(value.name))
                elif hasattr(value, 'id'):
                    row.append(str(value.id))
                else:
                    row.append(str(value))
            text += "| " + " | ".join(row) + " |\n"
        
        return text