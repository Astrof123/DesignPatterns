import datetime
import unittest
from src.dtos.filter_dto import FilterDto
from src.repository import Repository
from src.core.prototype import Prototype
from src.logics.prototype_report import PrototypeReport
from src.start_service import StartService
from src.core.validator import OperationException


class TestPrototype(unittest.TestCase):

    def test_any_prototype_filter(self):
        # Подготовка

        start = StartService()
        start.start()
        start_prototype = PrototypeReport(start.transactions)
        start_date = datetime.datetime.strptime("2025-10-28", "%Y-%m-%d").date()

        # Действие
        next_prototype = start_prototype.filter_up_startdate(start_prototype, start_date)
        
        # Проверка
        assert len(next_prototype.data) > 0
        assert len(start_prototype.data) > 0
        assert len(start_prototype.data) >= len(next_prototype.data)


    def test_any_protype_universal_filter(self):
         # Подготовка

        start = StartService()
        start.start()
        start_prototype = PrototypeReport(start.transactions)
        start_date = datetime.datetime.strptime("2025-10-28", "%Y-%m-%d").date()

        dto = FilterDto()
        dto.field_name = "date"
        dto.value = start_date

        # Действие
        next_prototype = start_prototype.filter(start_prototype, dto)
        
        # Проверка
        assert len(next_prototype.data) == 1     


if __name__ == "__main__":
    unittest.main()