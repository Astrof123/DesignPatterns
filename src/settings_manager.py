from src.models.company_model import CompanyModel
import json
import os

class SettingsManager:
    __file_name:str = ""
    __company: CompanyModel = None


    def __new__(cls, file_name: str):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SettingsManager, cls).__new__(cls)

        return cls.instance

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.default()


    @property
    def company_setting(self) -> CompanyModel:
        return self.__company


    @property
    def file_name(self) -> str:
        return self.__file_name

    @file_name.setter
    def file_name(self, value: str):
        if value.strip() == "":
            return 

        if os.path.exists(value):
            self.__file_name = value.strip()

    
    def load(self):
        if self.__file_name.strip == "":
            raise FileNotFoundError("Не найден файл настроек!")

        try:
            file = open(self.__file_name)
            data = json.load(file)

            if "company" in data:
                item = data["company"]
                self.__company.name = item["name"] 
                return True

            return False

        except:
            return False


    def default(self):
        self.__company = CompanyModel()
        self.__company.name = "Ромашка"