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


    def test_check_companies_settings(self):
        # Подготовка
        filename = "settings.json"
        manager1 = SettingsManager(filename)
        manager2 = SettingsManager(filename)

        manager1.load()
        # manager2.load()

        # Проверка
        assert manager1.company_setting == manager2.company_setting


if __name__ == "__main__":
    unittest.main()