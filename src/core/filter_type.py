
# Статический класс для хранения типов фильтров
class FilterType:
    
    @staticmethod
    def equals() -> str:
        return "equals"
    
    @staticmethod
    def like() -> str:
        return "like"

    @staticmethod
    def less() -> str:
        return "less"
    
    @staticmethod
    def greater() -> str:
        return "greater"
    
    @staticmethod
    def less_or_equal() -> str:
        return "less_or_equal"
    
    @staticmethod
    def greater_or_equal() -> str:
        return "greater_or_equal"
    
    @staticmethod
    def not_equals() -> str:
        return "not_equals"


    """Получить все доступные типы фильтров"""
    @classmethod
    def get_all_types(cls) -> list[str]:
        return [method() for method in cls.__dict__.values() 
                if isinstance(method, staticmethod) 
                and callable(method)]