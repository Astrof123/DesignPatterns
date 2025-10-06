from src.models.group_nomenclature_model import GroupNomenclature
from src.repository import Repository
from src.models.unit_measurement_model import UnitMeasurement
from src.models.nomenclature_model import Nomenclature


class StartService():
    __repository: Repository = Repository()
    
    def __init__(self):
        self.__repository.data[Repository.unit_measure_key] = {}
        self.__repository.data[Repository.group_nomenclature_key] = {}
        self.__repository.data[Repository.nomenclature_key] = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StartService, cls).__new__(cls)

        return cls.instance
    

    def __default_create_units_measure(self):
        gramm = UnitMeasurement.create_gramm()
        self.__repository.data[Repository.unit_measure_key]["грамм"] = gramm
        self.__repository.data[Repository.unit_measure_key]["кг"] = UnitMeasurement.create_kill(gramm)


    def __default_create_group_nomenclature(self):
        ingredients = GroupNomenclature()
        self.__repository.data[Repository.group_nomenclature_key]["ингредиенты"] = ingredients


    def __default_create_nomenclature(self):
        ingredients = self.__repository.data[Repository.group_nomenclature_key]["ингредиенты"]
        gramm = self.__repository.data[Repository.unit_measure_key]["грамм"]

        wheat_flour = Nomenclature()
        wheat_flour.name = "пшеничная мука"
        wheat_flour.full_name = "пшеничная мука"
        wheat_flour.group_nomenclature = ingredients
        wheat_flour.unit_measurement = gramm

        self.__repository.data[Repository.nomenclature_key]["пшеничная мука"] = wheat_flour

    '''
    Основной метод для генерации эталонных данных
    '''
    def start(self):
        self.__default_create_units_measure()
        self.__default_create_group_nomenclature()


    '''
    Стартовый набор данных
    '''
    @property
    def data(self):
        return self.__repository.data