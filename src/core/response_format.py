# Форматы ответов
class ResponseFormats:
    
    # Возвращает идентификатор формата CSV
    @staticmethod
    def csv() -> str:
        return "csv"
    
    # Возвращает идентификатор формата Excel
    @staticmethod
    def excel() -> str:
        return "excel"
    
    # Возвращает идентификатор формата JSON
    @staticmethod
    def json() -> str:
        return "json"
    
    # Возвращает идентификатор формата Markdown
    @staticmethod
    def markdown() -> str:
        return "markdown"
    
    # Возвращает идентификатор формата XML
    @staticmethod
    def xml() -> str:
        return "xml"
    
    # Возвращает список всех поддерживаемых форматов
    # Returns:
    #     list[str]: Список идентификаторов всех форматов
    @classmethod
    def get_all_formats(cls) -> list[str]:
        return [method() for method in cls.__dict__.values() 
                if isinstance(method, staticmethod) 
                and callable(method)]