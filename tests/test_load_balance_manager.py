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

            # Чередуем приход и расход для реалистичности
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

    def test_performance_with_block_period_shift(self):
        """Тест производительности при последовательном сдвиге block_period"""
        print("\n" + "=" * 60)
        print("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПРИ СДВИГЕ BLOCK_PERIOD")
        print("=" * 60)

        # Начальные параметры
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 12, 31)
        total_days = (end_date - start_date).days

        # Создаем менеджер балансов с начальной датой блокировки
        initial_block_period = start_date
        balances_manager = BalancesManager(self.__large_data_set, initial_block_period)

        print(f"\nОбщее количество транзакций: {len(self.__large_data_set[Repository.transaction_key])}")
        print(f"Период тестирования: с {start_date} по {end_date} ({total_days} дней)")
        print(f"Шаг сдвига: 30 дней")

        results = []

        # Последовательно сдвигаем block_period и замеряем время
        current_date = start_date
        step_days = 30  # Сдвигаем на 30 дней каждый раз

        while current_date <= end_date:
            # Устанавливаем новую дату блокировки
            balances_manager.block_period = current_date

            # Замер времени расчета балансов
            start_time = time.time()
            balances = balances_manager.calculation_balances_up_blocking_date()
            end_time = time.time()

            execution_time = end_time - start_time

            # Собираем статистику
            transactions_count = self.__count_transactions_before_date(
                self.__large_data_set[Repository.transaction_key],
                current_date
            )

            result = {
                'block_period': current_date,
                'execution_time': execution_time,
                'balances_count': len(balances),
                'transactions_included': transactions_count,
                'total_transactions': len(self.__large_data_set[Repository.transaction_key])
            }
            results.append(result)

            print(f"Block period: {current_date} | "
                  f"Время: {execution_time:.4f} сек | "
                  f"Транзакций учтено: {transactions_count}/{result['total_transactions']}")

            # Сдвигаем дату
            current_date += timedelta(days=step_days)


        # Проверяем, что все расчеты завершились успешно
        for result in results:
            self.assertIsInstance(balances, list)
            self.assertGreaterEqual(result['execution_time'], 0)

    def __count_transactions_before_date(self, transactions_dict, target_date):
        """Подсчет транзакций до указанной даты"""
        count = 0
        for transaction in transactions_dict.values():
            if transaction.date < target_date:
                count += 1
        return count


if __name__ == '__main__':
    # Запуск нагрузочного теста с подробным выводом
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBalancesManagerPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)