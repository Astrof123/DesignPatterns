
class CompanyModel:
    __name: str = ""
    __inn: str = ""

    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> str:
        if value.strip() != "":
            self.__name = value.strip()