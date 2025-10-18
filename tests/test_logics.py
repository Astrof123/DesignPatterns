import unittest

from src.logics.response_csv import ResponseCsv
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.logics.factory_entities import FactoryEntities
from src.core.response_format import ResponseFormats
from src.core.validator import Validator
from src.core.abstract_response import AbstractResponse

class TestStorageModel(unittest.TestCase):

    # Проверим формирование CSV
    def test_not_none_response_csv_build():
        # Подготовка
        response = ResponseCsv()
        data = []
        entity = GroupNomenclatureModel.create("test")
        data.append(entity)
        
        # Действие
        result = response.create("csv",)
        
        # Проверка
        assert result is not None

    def test_not_none_factory_create():
        # Подготовка
        factory = FactoryEntities()
        data = []
        entity = GroupNomenclatureModel.create("test")
        data.append(entity)

        # Действие
        logic = factory.create(ResponseFormats.csv)

        assert logic is not None
        instance = eval(logic)

        Validator.validate(instance, AbstractResponse)
        text = instance.build(ResponseFormats.csv, data)

        assert len(text) > 0

