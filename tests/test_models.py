from src.settings_manager import SettingsManager
from src.models.company_model import CompanyModel
import unittest


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


    def test_load_settings_from_different_location(self):
        # Подготовка
        filepath = "tests/test_data/test_settings.json"
        manager = SettingsManager(filepath)
        manager.load()

        # Проверяем, что настройки загрузились правильно
        assert manager.settings.company.name == "Тестовая Компания из другого места"
        assert manager.settings.company.INN == "123456789012"


    def test_check_company_is_none(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)
        manager.settings.company = None

        assert manager.settings.company == None

if __name__ == "__main__":
    unittest.main()