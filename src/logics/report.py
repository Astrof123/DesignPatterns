from src.dtos.filter_sorting_dto import FilterSortingDto
from src.core.prototype import Prototype
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
    def generateReport(self, storage, start_date, end_date, filtersDto = None, filter_model = None) -> list:
        nomenclatures: List[NomenclatureModel] = list(self.data[Repository.nomenclature_key].values())

        if filtersDto is not None and filter_model == "nomenclature":
            prototype = Prototype(nomenclatures)
        
            nomenclatures = prototype.filter(prototype, filtersDto).data

        report = []

        for nomenclature in nomenclatures:
            balance = self.calculateBalance(nomenclature, storage, start_date, end_date, filtersDto, filter_model)

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
    def calculateBalance(self, nomenclature, storage, start_date, end_date, filtersDto = None, filter_model = None):
        transactions: List[TransactionModel] = list(self.data[Repository.transaction_key].values())

        if filtersDto is not None and filter_model == "transaction":
            prototype = Prototype(transactions)
        
            transactions = prototype.filter(prototype, filtersDto).data


        report_prototype = Prototype(transactions)

        by_nomenclature_and_storage = FilterSortingDto([
            {
                "field_name": "nomenclature/id",
                "value": nomenclature.id,
                "type": "equals"
            },
            {
                "field_name": "storage/id",
                "value": storage.id,
                "type": "equals"
            }
        ], [])

        report_prototype = report_prototype.filter(report_prototype, by_nomenclature_and_storage)

        up_startdate = FilterSortingDto([
            {
                "field_name": "date",
                "value": start_date,
                "type": "less"
            }
        ], [])

        between_startdate_end_date = FilterSortingDto([
            {
                "field_name": "date",
                "value": start_date,
                "type": "greater_or_equal"
            },
            {
                "field_name": "date",
                "value": end_date,
                "type": "less_or_equal"
            }
        ], [])

        transactions_up_startdate = report_prototype.filter(report_prototype, up_startdate)
        transactions_between_startdate_end_date = report_prototype.filter(report_prototype, between_startdate_end_date)

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
