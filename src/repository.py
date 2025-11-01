class Repository:
    __data= {}
    
    unit_measure_key: str = "unit_measure"
    group_nomenclature_key: str = "group_nomenclature"
    nomenclature_key: str = "nomenclature"
    recipe_key: str = "recipe"
    transaction_key: str = "transaction"
    storage_key: str = "storage"

    @property
    def data(self):
        return self.__data
    
    # Получить список ключевых полей данных
    def get_key_fields(self):
        return [attr[:-4] for attr in dir(self) 
                if not attr.startswith('_') 
                and not callable(getattr(self, attr))
                and attr.endswith('_key')]
    