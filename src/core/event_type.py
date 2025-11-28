
"""
Типы событий
"""
class EventType:
    """
    Событие - смена даты блокировки
    """
    @staticmethod
    def change_block_period_key() -> str:
        return "change_block_period"


    """
    Событие - конвертация json
    """
    @staticmethod
    def convert_to_json() -> str:
        return "convert_to_json"


    # Получить список всех событий
    def events(self):
        return [attr[:-4] for attr in dir(self) 
                if not attr.startswith('_') 
                and not callable(getattr(self, attr))
                and attr.endswith('_key')]    