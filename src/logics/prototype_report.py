from datetime import date
from src.core.prototype import Prototype
from src.models.nomenclature_model import NomenclatureModel
from src.core.validator import Validator
from src.dtos.filter_dto import FilterDto

# Реализация прототипа
class PrototypeReport(Prototype):

    # Сделать фильтр по начальной дате
    # Возврат - прототип
    @staticmethod
    def filter_up_startdate(source: Prototype, start_date: date) -> Prototype:
        Validator.validate(source, Prototype)
        Validator.validate(start_date, date)

        result = []

        for item in source.data:
            if item.date < start_date:
                result.append(item)

        return source.clone(result)
    

    @staticmethod
    def filter_between_startdate_end_date(source: Prototype, start_date: date, end_date: date) -> Prototype:
        Validator.validate(source, Prototype)
        Validator.validate(start_date, date)
        Validator.validate(end_date, date)

        result = []

        for item in source.data:
            if item.date >= start_date and item.date <= end_date:
                result.append(item)

        return source.clone(result)
    

    @staticmethod
    def filter(source: Prototype, filter: FilterDto) -> Prototype:
        Validator.validate(source, Prototype)
        result = Prototype.filter(source.data, filter)
        
        return source.clone(result)