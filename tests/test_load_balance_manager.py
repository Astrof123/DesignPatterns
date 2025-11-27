# test_balances_manager_performance.py
import unittest
import datetime
import time
import random
from datetime import date, timedelta
from src.logics.balances_manager import BalancesManager
from src.models.storage_model import StorageModel
from src.models.nomenclature_model import NomenclatureModel
from src.models.transaction_model import TransactionModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.repository import Repository
from src.start_service import StartService


class TestBalancesManagerPerformance(unittest.TestCase):
    __start_service: StartService = None
    __large_data_set: dict = None
    __transactions_count: int = 3000
    
    def setUp(self):
        """Создание большого набора данных для нагрузочного тестирования"""
        self.__start_service = StartService()
        self.__start_service.start(True)
        self.__large_data_set = self.__create_large_dataset(self.__transactions_count)
        
    def __create_large_dataset(self, transaction_count):
        """Создание большого набора транзакций"""
        data = self.__start_service.data.copy()
        
        # Очищаем существующие транзакции
        data[Repository.transaction_key] = {}
        
        # Получаем доступные номенклатуры и склады
        nomenclatures = list(data[Repository.nomenclature_key].values())
        storages = list(data[Repository.storage_key].values())
        units = list(data[Repository.unit_measure_key].values())
        
        if not nomenclatures or not storages or not units:
            raise ValueError("Недостаточно данных для создания тестового набора")
        
        # Создаем большое количество транзакций
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 12, 31)
        total_days = (end_date - start_date).days
        
        print(f"\nСоздание {transaction_count} транзакций с {start_date} по {end_date}...")
        
        for i in range(transaction_count):
            # Равномерно распределяем транзакции по всему периоду
            transaction_date = start_date + timedelta(days=(i * total_days) // transaction_count)
            
            nomenclature = nomenclatures[i % len(nomenclatures)]
            storage = storages[i % len(storages)]
            unit = units[i % len(units)]
            

            quantity = 100.0 + (i * 10) % 500  # Базовое количество
            if i % 3 == 0:  # Каждая третья транзакция - расход
                quantity = -quantity
            
            transaction = TransactionModel(
                transaction_date,
                nomenclature,
                storage,
                quantity,
                unit
            )
            
            data[Repository.transaction_key][transaction.id] = transaction
        
        print(f"Создано {len(data[Repository.transaction_key])} транзакций")
        return data
    
    def test_performance_balances_by_date_with_shifting_block_period(self):
        """Тест производительности calculation_balances_by_date при сдвиге block_period"""
        
        # Параметры тестирования
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 12, 31)  # Конечная дата для расчета балансов
        target_date = end_date  # Всегда рассчитываем балансы на конец года
        
        # Создаем менеджер балансов с начальной датой блокировки
        initial_block_period = start_date
        balances_manager = BalancesManager(self.__large_data_set, initial_block_period)
        
        print(f"\nКонфигурация теста:")
        print(f"  Всего транзакций: {len(self.__large_data_set[Repository.transaction_key])}")
        print(f"  Период транзакций: {start_date} - {end_date}")
        print(f"  Целевая дата для расчета: {target_date}")
        print(f"  Дата блокировки сдвигается с шагом 1 месяц")
        
        results = []
        
        # Последовательно сдвигаем block_period на начало каждого месяца
        current_block_period = start_date
        month_step = 30 
        
        while current_block_period <= end_date:
            balances_manager.block_period = current_block_period
            

            print(f"\nУстановка block_period = {current_block_period}")
            start_time_base = time.time()
            base_balances = balances_manager.calculation_balances_up_blocking_date()
            base_time = time.time() - start_time_base
            print(f"  Базовые балансы рассчитаны за {base_time:.4f} сек")
            
            start_time_target = time.time()
            target_balances = balances_manager.calculation_balances_by_date(target_date)
            target_time = time.time() - start_time_target
            
            # Статистика для анализа
            transactions_after_block = self.__count_transactions_in_period(
                self.__large_data_set[Repository.transaction_key], 
                current_block_period, 
                target_date
            )
            
            transactions_before_block = self.__count_transactions_before_date(
                self.__large_data_set[Repository.transaction_key], 
                current_block_period
            )
            
            result = {
                'block_period': current_block_period,
                'base_calculation_time': base_time,  # Время расчета базовых балансов
                'target_calculation_time': target_time,  # Время calculation_balances_by_date
                'transactions_before_block': transactions_before_block,
                'transactions_after_block': transactions_after_block,
                'total_transactions': len(self.__large_data_set[Repository.transaction_key]),
                'target_balances_count': len(target_balances),
                'period_days': (target_date - current_block_period).days
            }
            results.append(result)
            
            print(f"  calculation_balances_by_date({target_date}): {target_time:.4f} сек")
            print(f"  Период для расчета: {result['period_days']} дней")
            
            # Сдвигаем дату блокировки на следующий месяц
            current_block_period += timedelta(days=month_step)
        
        
        # Проверяем корректность результатов
        for result in results:
            self.assertIsInstance(target_balances, list)
            self.assertGreaterEqual(result['target_calculation_time'], 0)
    
    def __count_transactions_in_period(self, transactions_dict, start_date, end_date):
        """Подсчет транзакций в указанном периоде (включительно)"""
        count = 0
        for transaction in transactions_dict.values():
            if start_date <= transaction.date <= end_date:
                count += 1
        return count
    
    def __count_transactions_before_date(self, transactions_dict, target_date):
        """Подсчет транзакций до указанной даты (исключая саму дату)"""
        count = 0
        for transaction in transactions_dict.values():
            if transaction.date < target_date:
                count += 1
        return count
    
   

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBalancesManagerPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)