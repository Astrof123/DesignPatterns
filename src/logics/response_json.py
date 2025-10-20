from src.core.abstract_response import AbstractResponse
import json

class ResponseJson(AbstractResponse):

    def __init__(self):
        super().__init__()

    def build(self, format: str, data: list):
        super().build(format, data)
            
        result = []
        for item in data:
            item_dict = {}
            
            # Получаем все атрибуты объекта (исключая приватные и методы)
            attributes = [attr for attr in dir(item) 
                         if not attr.startswith('_') 
                         and not callable(getattr(item, attr))]
            
            for attr in attributes:
                try:
                    value = getattr(item, attr)
                    
                    # Обрабатываем вложенные объекты
                    if hasattr(value, '__dict__'):
                        # Рекурсивно преобразуем вложенные объекты
                        nested_dict = {}
                        nested_attrs = [nested_attr for nested_attr in dir(value) 
                                      if not nested_attr.startswith('_') 
                                      and not callable(getattr(value, nested_attr))]
                        for nested_attr in nested_attrs:
                            nested_value = getattr(value, nested_attr)
                            if not callable(nested_value):
                                nested_dict[nested_attr] = self._convert_value(nested_value)
                        item_dict[attr] = nested_dict
                    else:
                        item_dict[attr] = self._convert_value(value)
                        
                except Exception:
                    continue
            
            result.append(item_dict)
                
        return json.dumps(result, ensure_ascii=False, indent=2)
    

    def _convert_value(self, value):
        if hasattr(value, 'isoformat'):  # datetime и подобные
            return value.isoformat()
        elif hasattr(value, '__str__'):
            return str(value)
        return value