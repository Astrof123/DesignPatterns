# Форматы ответов
class ResponseFormats:
    @staticmethod
    def csv() -> str:
        return "csv"
    
    @staticmethod
    def excel() -> str:
        return "excel"
    
    @staticmethod
    def json() -> str:
        return "json"
    
    @staticmethod
    def markdown() -> str:
        return "markdown"
    
    @staticmethod
    def xml() -> str:
        return "xml"
    
    @classmethod
    def get_all_formats(cls):
        return [method() for method in cls.__dict__.values() 
                if isinstance(method, staticmethod) 
                and callable(method.__func__)]