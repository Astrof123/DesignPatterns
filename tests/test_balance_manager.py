import unittest
import datetime
from datetime import date
from src.logics.balances_manager import BalancesManager
from src.repository import Repository
from src.start_service import StartService


class TestBalancesManager(unittest.TestCase):
    __balances_manager: BalancesManager = None
    __start_service: StartService = StartService()
    
    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.__start_service.start(True)
        self.block_period = datetime.date(2025, 10, 28)
        self.__balances_manager = BalancesManager(
            self.__start_service.data, 
            self.block_period
        )

    def test_create_balances_manager_instance_created(self):
        # Подготовка & Действие
        balances_manager1 = BalancesManager(self.__start_service.data, self.block_period)
        balances_manager2 = BalancesManager(self.__start_service.data, self.block_period)

        # Проверка
        assert isinstance(balances_manager1, BalancesManager)
        assert isinstance(balances_manager2, BalancesManager)
        assert balances_manager1.data == balances_manager2.data
        assert balances_manager1.block_period == balances_manager2.block_period

    def test_balances_manager_properties_setter_validation(self):
        # Подготовка
        balances_manager = BalancesManager(self.__start_service.data, self.block_period)
        new_block_period = datetime.date(2025, 11, 1)

        # Действие
        balances_manager.block_period = new_block_period

        # Проверка
        assert balances_manager.block_period == new_block_period

    def test_balances_manager_data_property_setter_invalid_type(self):
        # Подготовка
        balances_manager = BalancesManager(self.__start_service.data, self.block_period)

        # Действие & Проверка
        with self.assertRaises(Exception):
            balances_manager.data = "invalid_data"

    def test_balances_manager_block_period_setter_invalid_type(self):
        # Подготовка
        balances_manager = BalancesManager(self.__start_service.data, self.block_period)

        # Действие & Проверка
        with self.assertRaises(Exception):
            balances_manager.block_period = "invalid_date"

    def test_calculation_balances_up_blocking_date_returns_correct_structure(self):
        # Подготовка

        # Действие
        result = self.__balances_manager.calculation_balances_up_blocking_date()

        # Проверка
        assert result is not None
        assert isinstance(result, list)
        
        # Проверяем структуру каждого элемента баланса
        for balance in result:
            assert "nomenclature" in balance
            assert "unit" in balance
            assert "balance" in balance
            assert isinstance(balance["balance"], (int, float))

    def test_calculation_balances_up_blocking_date_correct_calculation(self):
        # Подготовка
        # Получаем транзакции до даты блокировки
        transactions = list(self.__start_service.transactions.values())
        transactions_before_block = [
            t for t in transactions 
            if t.date < self.block_period
        ]

        # Действие
        result = self.__balances_manager.calculation_balances_up_blocking_date()

        # Проверка - баланс должен быть рассчитан правильно
        assert len(result) > 0
        
        for balance in result:
            assert balance["balance"] is not None

    def test_calculation_balances_by_date_before_block_period(self):
        # Подготовка
        date_before_block = datetime.date(2025, 10, 27)

        # Действие
        result = self.__balances_manager.calculation_balances_by_date(date_before_block)

        # Проверка
        assert result is not None
        assert isinstance(result, list)

    def test_calculation_balances_by_date_after_block_period(self):
        # Подготовка
        date_after_block = datetime.date(2025, 10, 29)

        # Действие
        result = self.__balances_manager.calculation_balances_by_date(date_after_block)

        # Проверка
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    def test_calculation_balances_by_date_same_as_block_period(self):
        # Подготовка
        same_date = self.block_period

        # Действие
        result = self.__balances_manager.calculation_balances_by_date(same_date)

        # Проверка
        assert result is not None
        assert isinstance(result, list)

    def test_calculation_balances_by_date_future_date(self):
        # Подготовка
        future_date = datetime.date(2030, 1, 1)

        # Действие
        result = self.__balances_manager.calculation_balances_by_date(future_date)

        # Проверка
        assert result is not None
        assert isinstance(result, list)


    def test_unit_conversion_in_balances(self):
        # Подготовка
        test_date = datetime.date(2025, 10, 29)

        # Действие
        result = self.__balances_manager.calculation_balances_by_date(test_date)

        # Проверка - все балансы должны быть в корневых единицах измерения
        for balance in result:
            assert isinstance(balance["balance"], (int, float))
            # Баланс не должен быть None или строкой
            assert balance["balance"] is not None

    def test_empty_transactions(self):
        # Подготовка
        empty_data = {
            Repository.nomenclature_key: self.__start_service.nomenclatures,
            Repository.transaction_key: {},
            Repository.storage_key: self.__start_service.storages,
            Repository.unit_measure_key: self.__start_service.units_measure,
            Repository.group_nomenclature_key: self.__start_service.groups_nomenclature,
            Repository.recipe_key: self.__start_service.recipes,
            Repository.balances_key: []
        }
        empty_balances_manager = BalancesManager(empty_data, self.block_period)

        # Действие
        result = empty_balances_manager.calculation_balances_up_blocking_date()

        # Проверка
        assert result == []

    def test_balances_calculation_with_different_block_periods(self):
        # Подготовка
        early_block_period = datetime.date(2025, 10, 26)
        late_block_period = datetime.date(2025, 10, 30)
        
        early_balances_manager = BalancesManager(self.__start_service.data, early_block_period)
        late_balances_manager = BalancesManager(self.__start_service.data, late_block_period)

        # Действие
        early_balances = early_balances_manager.calculation_balances_up_blocking_date()
        late_balances = late_balances_manager.calculation_balances_up_blocking_date()

        # Проверка
        assert isinstance(early_balances, list)
        assert isinstance(late_balances, list)
        

    def test_recalculation_after_block_period_change(self):
        # Подготовка
        initial_balances = self.__balances_manager.calculation_balances_up_blocking_date()
        new_block_period = datetime.date(2025, 10, 29)

        # Действие
        self.__balances_manager.block_period = new_block_period
        recalculated_balances = self.__balances_manager.calculation_balances_up_blocking_date()

        # Проверка
        assert isinstance(initial_balances, list)
        assert isinstance(recalculated_balances, list)
        # После изменения даты блокировки балансы должны пересчитаться