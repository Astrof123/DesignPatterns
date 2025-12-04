
import json
from src.core.observe_service import ObserveService
from src.logics.factory_entities import FactoryEntities
from src.core.event_type import EventType
from src.repository import Repository


class DataManager:
    __data = None
    __factory = FactoryEntities()


    def __init__(self, data):
        self.__data = data
        ObserveService.add(self)

    """
    Сохраняет данные в json файл
    """
    def save_data_to_file(self, filename="data/data.json"):
        prepared_data = self.prepare_data(self.__data, self.__factory)
        
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

            data_to_json = None
            if field == "balances":
                data_to_json = data[field]
            else:
                data_to_json = list(data[field].values())

            result = logic().build("json", data_to_json)
            prepared_data[field] = result

        return prepared_data
    
    def handle(self, event: str, params):
        """
        Обработчик событий
        """
        if event == EventType.change_reference_type_key():
            self.save_data_to_file("data/data.json")