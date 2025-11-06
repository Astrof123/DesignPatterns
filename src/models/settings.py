
from src.models.company_model import CompanyModel
from src.core.validator import ArgumentException, Validator

class Settings:
    __company: CompanyModel = None
    __response_format: str = "CSV"
    __first_start: bool = True

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