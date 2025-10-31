
from src.models.nomenclature_model import NomenclatureModel
from src.models.transaction_model import TransactionModel
from src.repository import Repository
from src.core.validator import Validator
from typing import List, Dict, Set, Tuple


class Report:
    __data: dict

    def __init__(self, data):
        self.data = data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: dict):
        Validator.validate(value, dict)
        self.__data = value

    """
    Генерирует отчет
    """
    def generateReport(self, storage, start_date, end_date) -> list:
        nomenclatures: List[NomenclatureModel] = list(self.data[Repository.nomenclature_key].values())
        report = []

        for nomenclature in nomenclatures:
            balance = self.calculateBalance(nomenclature, storage, start_date, end_date)

            start_balance = balance[0]
            income = balance[1]
            outcome = balance[2]

            row = {
                "nomenclature": nomenclature.name,
                "unit": nomenclature.unit_measurement.root_base_unit().name,
                "start_balance": start_balance,
                "income": income,
                "outcome": outcome,
                "end_balance": start_balance + income - outcome
            }

            report.append(row)

        return report


    """
    Рассчитывает баланс по номенклатуре
    """
    def calculateBalance(self, nomenclature, storage, start_date, end_date):
        transactions: List[TransactionModel] = list(self.data[Repository.transaction_key].values())
        start_balance = 0
        income = 0
        outcome = 0

        for transaction in transactions:
            if transaction.storage == storage and transaction.nomenclature == nomenclature:
                quantity = transaction.unit.convert_to_root_base_unit(transaction.quantity)
                
                if transaction.date < start_date:
                    start_balance += quantity
                if transaction.date >= start_date and transaction.date <= end_date and quantity > 0:
                    income += quantity
                if transaction.date >= start_date and transaction.date <= end_date and quantity < 0:
                    outcome += quantity * -1


        return [start_balance, income, outcome]
