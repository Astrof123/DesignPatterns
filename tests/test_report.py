# test_report.py
import unittest
import datetime
from src.logics.report import Report
from src.models.storage_model import StorageModel
from src.models.nomenclature_model import NomenclatureModel
from src.models.transaction_model import TransactionModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.repository import Repository
from src.start_service import StartService


class TestReport(unittest.TestCase):
    __report: Report = None
    __start_service: StartService = StartService()
    
    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.__start_service.start(True)
        self.__report = Report(self.__start_service.data)
        self.storage = list(self.__start_service.storages.values())[0]
        self.start_date = datetime.date(2025, 10, 28)
        self.end_date = datetime.date(2025, 10, 30)

    def test_create_report_instance_created(self):
        # Подготовка & Действие
        report1 = Report(self.__start_service.data)
        report2 = Report(self.__start_service.data)

        # Проверка
        assert isinstance(report1, Report)
        assert isinstance(report2, Report)
        assert report1.data == report2.data

    def test_report_data_property_setter_validation(self):
        # Подготовка
        report = Report(self.__start_service.data)
        new_data = {"test": "data"}

        # Действие
        report.data = new_data

        # Проверка
        assert report.data == new_data

    def test_report_data_property_setter_invalid_type(self):
        # Подготовка
        report = Report(self.__start_service.data)

        # Действие & Проверка
        with self.assertRaises(Exception):
            report.data = "invalid_data"

    def test_generate_report_returns_correct_structure(self):
        # Подготовка

        # Действие
        result = self.__report.generateReport(self.storage, self.start_date, self.end_date)

        # Проверка
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Проверяем структуру каждой строки отчета
        for row in result:
            assert "nomenclature" in row
            assert "unit" in row
            assert "start_balance" in row
            assert "income" in row
            assert "outcome" in row
            assert "end_balance" in row
            assert isinstance(row["nomenclature"], str)
            assert isinstance(row["unit"], str)
            assert isinstance(row["start_balance"], (int, float))
            assert isinstance(row["income"], (int, float))
            assert isinstance(row["outcome"], (int, float))
            assert isinstance(row["end_balance"], (int, float))

    def test_generate_report_contains_all_nomenclatures(self):
        # Подготовка
        nomenclatures_count = len(self.__start_service.nomenclatures)

        # Действие
        result = self.__report.generateReport(self.storage, self.start_date, self.end_date)

        # Проверка
        assert len(result) == nomenclatures_count

    def test_calculate_balance_returns_correct_values(self):
        # Подготовка
        nomenclature = list(self.__start_service.nomenclatures.values())[0]

        # Действие
        balance = self.__report.calculateBalance(nomenclature, self.storage, self.start_date, self.end_date)

        # Проверка
        assert balance is not None
        assert isinstance(balance, list)
        assert len(balance) == 3
        assert all(isinstance(x, (int, float)) for x in balance)

    def test_calculate_balance_start_balance_calculation(self):
        # Подготовка
        nomenclature = list(self.__start_service.nomenclatures.values())[0]
        early_date = datetime.date(2025, 10, 1)

        # Действие
        balance = self.__report.calculateBalance(nomenclature, self.storage, early_date, self.end_date)

        # Проверка
        assert balance[0] >= 0  # Начальный баланс не может быть отрицательным

    def test_calculate_balance_income_outcome_positive_values(self):
        # Подготовка
        nomenclature = list(self.__start_service.nomenclatures.values())[0]

        # Действие
        balance = self.__report.calculateBalance(nomenclature, self.storage, self.start_date, self.end_date)

        # Проверка
        assert balance[1] >= 0  # Income всегда положительный
        assert balance[2] >= 0  # Outcome всегда положительный (хранится как абсолютное значение)

    def test_generate_report_end_balance_calculation(self):
        # Подготовка

        # Действие
        result = self.__report.generateReport(self.storage, self.start_date, self.end_date)

        # Проверка
        for row in result:
            expected_end_balance = row["start_balance"] + row["income"] - row["outcome"]
            assert row["end_balance"] == expected_end_balance

    def test_calculate_balance_different_storage_returns_zero(self):
        # Подготовка
        nomenclature = list(self.__start_service.nomenclatures.values())[0]
        different_storage = StorageModel("Другой склад", "Улица Тестовая 1")

        # Действие
        balance = self.__report.calculateBalance(nomenclature, different_storage, self.start_date, self.end_date)

        # Проверка
        assert balance[0] == 0  # Начальный баланс
        assert balance[1] == 0  # Income
        assert balance[2] == 0  # Outcome

    def test_calculate_balance_date_filtering(self):
        # Подготовка
        nomenclature = list(self.__start_service.nomenclatures.values())[0]
        future_date = datetime.date(2030, 1, 1)

        # Действие - отчет за будущий период, когда нет транзакций
        balance = self.__report.calculateBalance(nomenclature, self.storage, future_date, future_date)

        # Проверка
        assert balance[1] == 0  # Income за период без транзакций
        assert balance[2] == 0  # Outcome за период без транзакций

    def test_generate_report_empty_data(self):
        # Подготовка
        empty_data = {
            Repository.nomenclature_key: {},
            Repository.transaction_key: {},
            Repository.storage_key: {}
        }
        empty_report = Report(empty_data)
        storage = StorageModel("Тестовый склад", "Адрес")

        # Действие
        result = empty_report.generateReport(storage, self.start_date, self.end_date)

        # Проверка
        assert result == []

    def test_calculate_balance_unit_conversion(self):
        # Подготовка
        # Берем номенклатуру, для которой есть транзакции в разных единицах измерения
        transactions = list(self.__start_service.transactions.values())
        if transactions:
            transaction = transactions[0]
            nomenclature = transaction.nomenclature

            # Действие
            balance = self.__report.calculateBalance(nomenclature, self.storage, self.start_date, self.end_date)

            # Проверка - баланс должен быть рассчитан в корневых единицах измерения
            assert balance[0] >= 0
            # Проверяем, что значения являются числами (успешная конвертация)
            assert isinstance(balance[0], (int, float))
            assert isinstance(balance[1], (int, float))
            assert isinstance(balance[2], (int, float))

    def test_generate_report_multiple_storages(self):
        # Подготовка
        storages = list(self.__start_service.storages.values())
        if len(storages) > 1:
            second_storage = storages[1]

            # Действие
            result1 = self.__report.generateReport(storages[0], self.start_date, self.end_date)
            result2 = self.__report.generateReport(second_storage, self.start_date, self.end_date)

            # Проверка - отчеты для разных складов могут отличаться
            assert isinstance(result1, list)
            assert isinstance(result2, list)
            # Количество номенклатур должно быть одинаковым
            assert len(result1) == len(result2)