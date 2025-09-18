
from src.models.company_model import CompanyModel


class Settings:
    __company: CompanyModel = None

    def __init__(self):
        self.company = CompanyModel()

    @property
    def company(self) -> CompanyModel:
        return self.__company

    @company.setter
    def company(self, value: CompanyModel):
        if isinstance(value, CompanyModel):
            self.__company = value
        else:
            raise ValueError("Ожидается экземпляр CompanyModel")
    