import datetime
from src.core.observe_service import ObserveService
from src.core.event_type import EventType
from src.models.storage_model import StorageModel
from src.models.transaction_model import TransactionModel
from src.models.ingredient_model import IngredientModel
from src.core.validator import OperationException, Validator
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.repository import Repository
from src.models.unit_measurement_model import UnitMeasurement
from src.models.nomenclature_model import NomenclatureModel
from src.models.recipe_model import RecipeModel

class StartService():
    __repository: Repository = Repository()
    
    def __init__(self):
        self.data[Repository.unit_measure_key] = {}
        self.data[Repository.group_nomenclature_key] = {}
        self.data[Repository.nomenclature_key] = {}
        self.data[Repository.recipe_key] = {}
        self.data[Repository.transaction_key] = {}
        self.data[Repository.storage_key] = {}
        self.data[Repository.balances_key] = []
        

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StartService, cls).__new__(cls)

        return cls.instance
    

    '''
    Метод для генерации эталонных единиц измерения
    '''
    def __default_create_units_measure(self):
        gramm = UnitMeasurement.create_gramm()
        self.units_measure["gramm"] = gramm
        self.units_measure["kg"] = UnitMeasurement.create_kilo(gramm)


    '''
    Метод для генерации эталонных групп номенклатур
    '''
    def __default_create_group_nomenclature(self):
        ingredients = GroupNomenclatureModel()
        ingredients.name = "ingredients"
        self.groups_nomenclature["ingredients"] = ingredients


    '''
    Метод для генерации эталонных номенклатур
    '''
    def __default_create_nomenclature(self):
        ingredients = self.groups_nomenclature["ingredients"]
        gramm = self.units_measure["gramm"]

        wheat_flour = NomenclatureModel("wheat flour", "wheat flour", ingredients, gramm)
        oatmeal = NomenclatureModel("oatmeal", "oatmeal", ingredients, gramm)
        sugar = NomenclatureModel("sugar", "granulated sugar", ingredients, gramm)
        butter = NomenclatureModel("butter", "butter", ingredients, gramm)
        chicken_egg = NomenclatureModel("chicken egg", "chicken egg", ingredients, gramm)
        dark_chocolate = NomenclatureModel("dark chocolate", "dark chocolate", ingredients, gramm)
        baking_powder = NomenclatureModel("baking powder", "baking powder", ingredients, gramm)
        salt = NomenclatureModel("salt", "salt", ingredients, gramm)

        self.nomenclatures["wheat_flour"] = wheat_flour
        self.nomenclatures["baking_powder"] = baking_powder
        self.nomenclatures["oatmeal"] = oatmeal
        self.nomenclatures["sugar"] = sugar
        self.nomenclatures["butter"] = butter
        self.nomenclatures["chicken_egg"] = chicken_egg
        self.nomenclatures["dark_chocolate"] = dark_chocolate
        self.nomenclatures["salt"] = salt

    '''
    Метод для создания рецепта печенья
    '''
    def create_cookies_recipe(self, wheat_flour, 
                              oatmeal, sugar, 
                              butter, chicken_egg, 
                              dark_chocolate, baking_powder, 
                              salt):
        
        Validator.validate_models(wheat_flour, NomenclatureModel, "wheat flour")
        Validator.validate_models(oatmeal, NomenclatureModel, "oatmeal")
        Validator.validate_models(sugar, NomenclatureModel, "sugar")
        Validator.validate_models(butter, NomenclatureModel, "butter")
        Validator.validate_models(chicken_egg, NomenclatureModel, "chicken egg")
        Validator.validate_models(dark_chocolate, NomenclatureModel, "dark chocolate")
        Validator.validate_models(baking_powder, NomenclatureModel, "baking powder")
        Validator.validate_models(salt, NomenclatureModel, "salt")


        description = """
            Время приготовления: 25 минут
            Духовку разогрейте до 180°C. Противень застелите бумагой для выпечки.
            Шоколад измельчите на небольшие кусочки ножом.
            Масло комнатной температуры взбейте с сахаром до легкой пены.
            Добавьте яйцо и взбивайте еще 1-2 минуты до однородности.
            В отдельной миске смешайте овсяные хлопья, муку, разрыхлитель и соль.
            Соедините сухие ингредиенты с масляной смесью, добавьте измельченный шоколад.
            Замесите тесто ложкой до однородной консистенции.
            Сформируйте небольшие шарики (примерно по 30-40 гр), выложите на противень и слегка приплюсните.
            Выпекайте 12-15 минут до золотистого края. Дайте печенью остыть на противне 5 минут перед подачей.
            Приятного аппетита!
        """

        cookies = RecipeModel("cookies", description)
        self.add_ingredient(cookies, wheat_flour, 100)
        self.add_ingredient(cookies, oatmeal, 200)
        self.add_ingredient(cookies, sugar, 150)
        self.add_ingredient(cookies, butter, 180)
        self.add_ingredient(cookies, chicken_egg, 55)
        self.add_ingredient(cookies, dark_chocolate, 100)
        self.add_ingredient(cookies, baking_powder, 5)
        self.add_ingredient(cookies, salt, 2)

        return cookies

    '''
    Метод для генерации эталонных рецептов
    '''
    def __default_create_recipes(self):
        cookies = self.create_cookies_recipe(
            self.nomenclatures["wheat_flour"],
            self.nomenclatures["oatmeal"],
            self.nomenclatures["sugar"],
            self.nomenclatures["butter"],
            self.nomenclatures["chicken_egg"],
            self.nomenclatures["dark_chocolate"],
            self.nomenclatures["baking_powder"],
            self.nomenclatures["salt"],
        )

        self.recipes["cookies"] = cookies

    '''
    Метод для генерации эталонных складов
    '''
    def __default_create_storages(self):
        storage1 = StorageModel("Первый склад", "Улица Мира 122")
        self.storages["Первый склад"] = storage1

        storage2 = StorageModel("Второй склад", "Улица Ленина 44")
        self.storages["Второй склад"] = storage2

    '''
    Метод для генерации эталонных транзакций
    '''
    def __default_create_transactions(self):
        transaction1 = TransactionModel(
            datetime.date(2025, 10, 29),
            self.nomenclatures["wheat_flour"],
            self.storages["Первый склад"],
            5.0,
            self.units_measure["kg"]
        )

        transaction2 = TransactionModel(
            datetime.date(2025, 10, 27),
            self.nomenclatures["baking_powder"],
            self.storages["Первый склад"],
            800.0,
            self.units_measure["gramm"]
        )

        transaction3 = TransactionModel(
            datetime.date(2025, 10, 28),
            self.nomenclatures["wheat_flour"],
            self.storages["Первый склад"],
            11.0,
            self.units_measure["kg"]
        )

        transaction4 = TransactionModel(
            datetime.date(2025, 10, 30),
            self.nomenclatures["wheat_flour"],
            self.storages["Первый склад"],
            -5.0,
            self.units_measure["kg"]
        )

        transaction5 = TransactionModel(
            datetime.date(2025, 10, 29),
            self.nomenclatures["baking_powder"],
            self.storages["Первый склад"],
            500.0,
            self.units_measure["gramm"]
        )

        transaction6 = TransactionModel(
            datetime.date(2025, 10, 30),
            self.nomenclatures["baking_powder"],
            self.storages["Первый склад"],
            -1100.0,
            self.units_measure["gramm"]
        )

        self.transactions[transaction1.id] = transaction1
        self.transactions[transaction2.id] = transaction2
        self.transactions[transaction3.id] = transaction3
        self.transactions[transaction4.id] = transaction4
        self.transactions[transaction5.id] = transaction5
        self.transactions[transaction6.id] = transaction6



    '''
    Добавление ингредиента в модель рецепта
    '''
    def add_ingredient(self, recipe: RecipeModel, ingredient: NomenclatureModel, count: int):
        Validator.validate_models(recipe, RecipeModel)
        Validator.validate_models(ingredient, NomenclatureModel)
        Validator.validate(count, int)

        recipe.ingredients.append(IngredientModel("Ингредиент: " + ingredient.name, ingredient, count))

    '''
    Основной метод для генерации эталонных данных
    '''
    def start(self, first_start):
        if first_start:
            self.__default_create_units_measure()
            self.__default_create_group_nomenclature()
            self.__default_create_nomenclature()
            self.__default_create_recipes()
            self.__default_create_storages()
            self.__default_create_transactions()

    '''
    Стартовый набор данных
    '''
    @property
    def data(self):
        return self.__repository.data
    
    """Список номенклатур"""
    @property
    def nomenclatures(self):
        return self.data[Repository.nomenclature_key]
    
    """Список единиц измерения"""
    @property
    def units_measure(self):
        return self.data[Repository.unit_measure_key]

    """Список групп номенклатур"""
    @property
    def groups_nomenclature(self):
        return self.data[Repository.group_nomenclature_key]
    
    """Список рецептов"""
    @property
    def recipes(self):
        return self.data[Repository.recipe_key]
    
    """Список транзакций"""
    @property
    def transactions(self):
        return self.data[Repository.transaction_key]
    
    """Список складов"""
    @property
    def storages(self):
        return self.data[Repository.storage_key]
    
    """Остатки"""
    @property
    def balances(self):
        return self.data[Repository.balances_key]
    
    @balances.setter
    def balances(self, value):
        Validator.validate(value, list)
        self.data[Repository.balances_key] = value
