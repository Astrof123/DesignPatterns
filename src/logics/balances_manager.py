from datetime import datetime, date
from typing import List

from src.logics.factory_convert import FactoryConvert
from src.dtos.filter_sorting_dto import FilterSortingDto
from src.core.prototype import Prototype
from src.repository import Repository
from src.core.validator import Validator
from src.models.transaction_model import TransactionModel
import copy

class BalancesManager:
    """Менеджер для расчета и управления остатками товаров на складах"""
    
    __block_period: date = None
    __data: dict
    __factory: FactoryConvert = FactoryConvert()

    def __init__(self, data, block_period):
        self.data = data
        self.block_period = block_period

    def calculation_balances_up_blocking_date(self):
        """Расчет балансов на дату блокировки
        
        Returns:
            List: Список балансов для каждой номенклатуры на дату блокировки
        """

        transactions: List[TransactionModel] = list(self.data[Repository.transaction_key].values())

        balance_prototype = Prototype(transactions)

        up_block_period = FilterSortingDto([
            {
                "field_name": "date",
                "value": self.block_period,
                "type": "less"
            }
        ], [])
        transactions_up_block_period = balance_prototype.filter(balance_prototype, up_block_period)

        balances = {}
        for transaction in transactions_up_block_period.data:
            quantity = transaction.unit.convert_to_root_base_unit(transaction.quantity)

            if transaction.nomenclature.id in balances:
                balances[transaction.nomenclature.id]["balance"] += quantity
            else:
                balances[transaction.nomenclature.id] = {
                    "nomenclature": self.__factory.convert(transaction.nomenclature),
                    "unit": self.__factory.convert(transaction.nomenclature.unit_measurement.root_base_unit()),
                    "balance": quantity,
                }

        self.data[Repository.balances_key] = list(balances.values())
        
        return list(balances.values())
    
    def calculation_balances_by_date(self, date):
        """Расчет балансов на произвольную дату
        
        Args:
            target_date: Дата, на которую нужно рассчитать балансы
            
        Returns:
            List: Список балансов для каждой номенклатуры на указанную дату
        """


        if self.data[Repository.balances_key] is None:
            self.calculation_balances_up_blocking_date()

        if self.block_period >= date:
            return list(self.data[Repository.balances_key].values())


        transactions: List[TransactionModel] = list(self.data[Repository.transaction_key].values())
        balance_prototype = Prototype(transactions)

        after_block_period = FilterSortingDto([
            {
                "field_name": "date",
                "value": self.block_period,
                "type": "greater_or_equal"
            },
            {
                "field_name": "date",
                "value": date,
                "type": "less_or_equal"
            }
        ], [])

        transactions_after_block_period = balance_prototype.filter(balance_prototype, after_block_period)

        balances_by_date = copy.deepcopy(self.data[Repository.balances_key])
        for transaction in transactions_after_block_period.data:
            quantity = transaction.unit.convert_to_root_base_unit(transaction.quantity)

            if transaction.nomenclature.id in balances_by_date:
                balances_by_date[transaction.nomenclature.id]["balance"] += quantity
            else:
                balances_by_date[transaction.nomenclature.id] = {
                    "nomenclature": self.__factory.convert(transaction.nomenclature),
                    "unit": self.__factory.convert(transaction.nomenclature.unit_measurement.root_base_unit()),
                    "balance": quantity,
                }

        return list(balances_by_date.values()) 


    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: dict):
        Validator.validate(value, dict)
        self.__data = value

    @property
    def block_period(self) -> date:
        return self.__block_period
    
    @block_period.setter
    def block_period(self, value: date):
        Validator.validate(value, date)
        self.__block_period = value