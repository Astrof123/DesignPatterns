
import json
from src.repository import Repository


class DataManager:

    """
    Сохраняет данные в json файл
    """
    def save_data_to_file(self, data, factory, filename="data/data.json"):
        prepared_data = self.prepare_data(data, factory)
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(prepared_data, file, ensure_ascii=False, indent=4)

            return True
        except Exception as e:
            return False


    """
    Подготавливает данные, приводя их в json формат
    """    
    def prepare_data(self, data, factory):
        all_fields = Repository.get_key_fields(Repository)

        prepared_data = {}

        for field in all_fields:
            logic = factory.create("json")
            result = logic().build("json", list(data[field].values()))
            prepared_data[field] = result

        return prepared_data