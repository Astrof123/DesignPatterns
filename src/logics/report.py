
from src.logics.prototype_report import PrototypeReport
from src.logics.factory_convert import FactoryConvert
from src.models.nomenclature_model import NomenclatureModel
from src.models.transaction_model import TransactionModel
from src.repository import Repository
from src.core.validator import Validator
from typing import List


class Report:
    __data: dict
    __factory: FactoryConvert = FactoryConvert()

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
                "nomenclature": self.__factory.convert(nomenclature),
                "unit": self.__factory.convert(nomenclature.unit_measurement.root_base_unit()),
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

        report_prototype = PrototypeReport(transactions)

        transactions_up_startdate = report_prototype.filter_up_startdate(report_prototype, start_date)
        transactions_between_startdate_end_date = report_prototype.filter_between_startdate_end_date(report_prototype, start_date, end_date)

        start_balance = 0
        income = 0
        outcome = 0

        for transaction in transactions_up_startdate.data:
            quantity = transaction.unit.convert_to_root_base_unit(transaction.quantity)
            start_balance += quantity

        for transaction in transactions_between_startdate_end_date.data:
            quantity = transaction.unit.convert_to_root_base_unit(transaction.quantity)
            if quantity > 0:
                income += quantity
            if quantity < 0:
                outcome += quantity * -1


        return [start_balance, income, outcome]
