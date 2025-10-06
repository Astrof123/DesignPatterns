import unittest
from src.models.unit_measurement_model import UnitMeasurement
from src.start_service import StartService
from src.repository import Repository

class TestStart(unittest.TestCase):
    __start_service: StartService = StartService()
    
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
        self.__start_service.start()

    def test_start_service_start_unit_not_empty(self):
        # Подготовка
        # Действие

        # Проверка
        assert len(self.__start_service.data[Repository.unit_measure_key]) > 0


    def test_start_service_eq_units(self):
        # Подготовка
        gram = self.__start_service.data[Repository.unit_measure_key]["gramm"]
        killo = self.__start_service.data[Repository.unit_measure_key]["kg"]
        # Действие

        # Проверка
        assert killo.base_unit.id == gram.id