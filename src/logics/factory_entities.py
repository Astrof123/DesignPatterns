from src.logics.response_json import ResponseJson
from src.logics.response_markdown import ResponseMarkdown
from src.logics.response_xml import ResponseXml
from src.models.settings import Settings
from src.logics.response_csv import ResponseCsv
from src.core.abstract_model import AbstractModel
from src.core.validator import Validator, OperationException

class FactoryEntities:
    __match = {
        "csv": ResponseCsv,
        "markdown": ResponseMarkdown,
        "json": ResponseJson,
        "xml": ResponseXml
    }


    def __init__(self, settings: Settings = None):
        self.__settings = settings


    def create(self, format: str) -> AbstractModel:
        if format not in self.__match.keys():
            raise OperationException("Формат не верный")
        
        return self.__match[format]
    

    def create_default(self):
        if self.__settings is None:
            raise OperationException("Настройки не установлены")
        
        format = self.__settings.response_format
        return self.create(format)    