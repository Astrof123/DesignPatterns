from src.models.group_nomenclature_model import GroupNomenclature
from src.models.nomenclature_model import Nomenclature
from src.core.validator import ArgumentException
from src.models.unit_measurement_model import UnitMeasurement
from src.models.storage_model import StorageModel
from src.settings_manager import SettingsManager
from src.models.company_model import CompanyModel
import unittest
import uuid

class TestCompanyModel(unittest.TestCase):

    # Проверка создания основной модели
    # Данные после создания должны быть пустыми
    def test_empty_create_company_model(self):
        # Подготовка
        model = CompanyModel()

        # Действие
        
        
        # Проверки
        assert model.name == ""


    # Проверка создания основной модели
    # Данные меняем. Данные должны быть.
    def test_not_empty_create_company_model(self):
        # Подготовка
        model = CompanyModel()
        
        # Действие
        model.name = "test"
        
        # Проверка
        assert model.name != ""


    def test_load_company_settings(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)

        result = manager.load()

        # Проверка
        assert result == True


    def test_check_company_settings(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)

        manager.load()

        # Проверка
        assert manager.settings.company.name != ""
        assert manager.settings.company.INN != ""
        assert manager.settings.company.correspondent_account != ""
        assert manager.settings.company.BIK != ""
        assert manager.settings.company.ownership_type != ""
        assert manager.settings.company.account != ""


    def test_check_companies_settings(self):
        # Подготовка
        filename = "settings.json"
        manager1 = SettingsManager(filename)
        manager2 = SettingsManager(filename)

        manager1.load()
        manager2.load()

        # Проверка
        assert manager1.settings.company == manager2.settings.company


    # Проверка на сравнение двух по значению одинаковых моделей
    def test_equals_storage_model_create(self):
        # Подготовка

        id = str(uuid.uuid4())
        storage1 = StorageModel()
        storage2 = StorageModel()

        # Действие GUID
        storage1.id = id
        storage2.id = id
        # Проверки


        assert storage1 == storage2


    def test_load_settings_from_different_location(self):
        # Подготовка
        filepath = "tests/test_data/test_settings.json"
        manager = SettingsManager(filepath)
        manager.load()

        # Проверяем, что настройки загрузились правильно
        assert manager.settings.company.name == "Тестовая Компания из другого места"
        assert manager.settings.company.INN == 123456789012


    def test_check_company_is_none(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)
        manager.settings.company = None

        # Проверка
        assert manager.settings.company == None


    def test_check_settings_wrong_file(self):
        # Подготовка
        filename = "settings.jsen"
        

        # Проверка
        with self.assertRaises(ArgumentException):
            manager = SettingsManager(filename)


    def test_check_companys_fields(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)
        manager.load()
        

        with self.assertRaises(ArgumentException):
            manager.settings.company.name = None

        manager.settings.company.name = "Ромашка"
        assert manager.settings.company.name == "Ромашка"


        with self.assertRaises(ArgumentException):
            manager.settings.company.INN = None

        with self.assertRaises(ArgumentException):
            manager.settings.company.INN = "12345678901"

        manager.settings.company.INN = "123456789012"
        assert manager.settings.company.INN == 123456789012

        manager.settings.company.INN = 123456789012
        assert manager.settings.company.INN == 123456789012


        with self.assertRaises(ArgumentException):
            manager.settings.company.account = None

        with self.assertRaises(ArgumentException):
            manager.settings.company.account = "4070281000"

        manager.settings.company.account = "40702810000"
        assert manager.settings.company.account == 40702810000

        manager.settings.company.account = 40702810000
        assert manager.settings.company.account == 40702810000


        with self.assertRaises(ArgumentException):
            manager.settings.company.correspondent_account = None

        with self.assertRaises(ArgumentException):
            manager.settings.company.correspondent_account = "3010181000"

        manager.settings.company.correspondent_account = 30101810000
        assert manager.settings.company.correspondent_account == 30101810000

        manager.settings.company.correspondent_account = 30101810000
        assert manager.settings.company.correspondent_account == 30101810000


        with self.assertRaises(ArgumentException):
            manager.settings.company.BIK = None

        with self.assertRaises(ArgumentException):
            manager.settings.company.BIK = "04452522"

        manager.settings.company.BIK = "144525225"
        assert manager.settings.company.BIK == 144525225

        manager.settings.company.BIK = 144525225
        assert manager.settings.company.BIK == 144525225


        with self.assertRaises(ArgumentException):
            manager.settings.company.ownership_type = None

        with self.assertRaises(ArgumentException):
            manager.settings.company.ownership_type = "000 А0О"

        manager.settings.company.ownership_type = "АО"
        assert manager.settings.company.ownership_type == "АО"


    def test_not_empty_create_unitmeasure_model(self):
        # Подготовка
        base_range = UnitMeasurement("грамм", 1)
        new_range = UnitMeasurement("кг", 1000, base_range)

        # Действие
        
        # Проверка
        assert base_range.name == "грамм"
        assert new_range.name == "кг"
        assert base_range.coefficient == 1
        assert new_range.coefficient == 1000
        assert base_range.base_unit == None
        assert new_range.base_unit == base_range


    def test_check_unitmeasure_fields(self):

        # Подготовка
        base_range = UnitMeasurement("грамм", 1)

        # Действие

        # Проверка
        with self.assertRaises(ArgumentException):
            base_range.name = 123

        with self.assertRaises(ArgumentException):
            base_range.name = None
        
        with self.assertRaises(ArgumentException):
            base_range.coefficient = None

        with self.assertRaises(ArgumentException):
            base_range.coefficient = "123"

        with self.assertRaises(ArgumentException):
            base_range.base_unit = "123"


    def test_check_nomenclature_fields(self):

        # Подготовка
        nomenclature_model = Nomenclature()

        # Действие
        nomenclature_model.name = "Хлеб"
        nomenclature_model.group_nomenclature = GroupNomenclature()
        nomenclature_model.unit_measurement = UnitMeasurement("грамм", 1)
        nomenclature_model.full_name = "Хлебобулочные изделия"


        # Проверка

        assert nomenclature_model.name == "Хлеб"

        with self.assertRaises(ArgumentException):
            nomenclature_model.name = 123

        with self.assertRaises(ArgumentException):
            nomenclature_model.name = "1" * 51
        

        assert nomenclature_model.group_nomenclature != None

        with self.assertRaises(ArgumentException):
            nomenclature_model.group_nomenclature = 123


        assert nomenclature_model.unit_measurement != None

        with self.assertRaises(ArgumentException):
            nomenclature_model.unit_measurement = 123


        assert nomenclature_model.full_name == "Хлебобулочные изделия"

        with self.assertRaises(ArgumentException):
            nomenclature_model.full_name = 123

        with self.assertRaises(ArgumentException):
            nomenclature_model.full_name = "1" * 256


if __name__ == "__main__":
    unittest.main()