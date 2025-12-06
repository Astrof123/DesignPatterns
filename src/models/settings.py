from src.models.company_model import CompanyModel
from src.core.validator import ArgumentException, Validator

class Settings:
    __company: CompanyModel = None
    __response_format: str = "CSV"
    __first_start: bool = True
    __log_level: str = "INFO"
    __log_mode: str = "console"
    __log_date_format: str = "%Y-%m-%d %H:%M:%S"
    __log_format: str = "{timestamp} | {level} | {source} | {message} | {data}"
    __log_directory: str = "logs"

    def __init__(self):
        self.company = CompanyModel()

    @property
    def company(self) -> CompanyModel:
        return self.__company

    @company.setter
    def company(self, value: CompanyModel|None):
        if isinstance(value, CompanyModel) or value is None:
            self.__company = value
        else:
            raise ArgumentException("Ожидается экземпляр CompanyModel")
    
    @property
    def response_format(self) -> str:
        return self.__response_format
    
    @response_format.setter
    def response_format(self, value: str):
        valid_formats = ["CSV", "Markdown", "Json", "XML"]
        if value in valid_formats:
            self.__response_format = value
        else:
            raise ArgumentException(f"Недопустимый формат. Допустимые значения: {valid_formats}")
        
    @property
    def first_start(self) -> bool:
        return self.__first_start
    
    @first_start.setter
    def first_start(self, value: bool):
        Validator.validate(value, bool)
        self.__first_start = value
    
    @property
    def log_level(self) -> str:
        return self.__log_level
    
    @log_level.setter
    def log_level(self, value: str):
        valid_levels = ["ERROR", "INFO", "DEBUG"]
        if value.upper() in valid_levels:
            self.__log_level = value.upper()
        else:
            raise ArgumentException(f"Недопустимый уровень логирования. Допустимые значения: {valid_levels}")
    
    @property
    def log_mode(self) -> str:
        return self.__log_mode
    
    @log_mode.setter
    def log_mode(self, value: str):
        valid_modes = ["console", "file", "both"]
        if value.lower() in valid_modes:
            self.__log_mode = value.lower()
        else:
            raise ArgumentException(f"Недопустимый режим логирования. Допустимые значения: {valid_modes}")
    
    @property
    def log_date_format(self) -> str:
        return self.__log_date_format
    
    @log_date_format.setter
    def log_date_format(self, value: str):
        Validator.validate(value, str)
        self.__log_date_format = value
    
    @property
    def log_format(self) -> str:
        return self.__log_format
    
    @log_format.setter
    def log_format(self, value: str):
        Validator.validate(value, str)
        self.__log_format = value
    
    @property
    def log_directory(self) -> str:
        return self.__log_directory
    
    @log_directory.setter
    def log_directory(self, value: str):
        Validator.validate(value, str)
        self.__log_directory = value