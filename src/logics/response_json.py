from src.logics.factory_convert import FactoryConvert
from src.core.abstract_response import AbstractResponse

class ResponseJson(AbstractResponse):
    factory_convert: FactoryConvert = FactoryConvert()


    def __init__(self):
        super().__init__()

    # Преобразует данные в формат JSON
    def build(self, format: str, data: list):
        super().build(format, data)
            
        result = []
        for item in data:
            item_dict = self.factory_convert.convert(item)
            
            result.append(item_dict)
                
        return result
    

