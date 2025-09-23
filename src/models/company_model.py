
class CompanyModel:
    __name: str = ""
    __INN: str = ""
    __account: str = ""
    __correspondent_account: str = ""
    __BIK: str = ""
    __ownership_type: str = ""

    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> str:

        if isinstance(value, str):
            if value.strip() != "":
                self.__name = value.strip()
            else:
                raise ValueError("Поле name не должно быть пустым")
        else:
            raise ValueError("Поле name должно быть строкой")

    @property
    def INN(self) -> str:
        return self.__INN
    
    @INN.setter
    def INN(self, value: str|int) -> str:
        if isinstance(value, (str, int)):
            if len(str(value).strip()) == 12:
                self.__INN = str(value).strip()
            else:
                raise ValueError("Поле INN должно быть длиной в 12 символов.")
        else:
            raise ValueError("Поле INN должно быть строкой или числом")

    @property
    def account(self) -> str:
        return self.__account
    
    @account.setter
    def account(self, value: str|int) -> str:
        if isinstance(value, (str, int)):
            if len(str(value).strip()) == 11:
                self.__account = str(value).strip()
            else:
                raise ValueError("Поле account должно быть длиной в 11 символов.")
        else:
            raise ValueError("Поле account должно быть строкой или числом")

    @property
    def correspondent_account(self) -> str:
        return self.__correspondent_account
    
    @correspondent_account.setter
    def correspondent_account(self, value: str|int) -> str:
        if isinstance(value, (str, int)):
            if len(str(value).strip()) == 11:
                self.__correspondent_account = str(value).strip()
            else:
                raise ValueError("Поле correspondent_account должно быть длиной в 11 символов.")
        else:
            raise ValueError("Поле correspondent_account должно быть строкой или числом")

    @property
    def BIK(self) -> str:
        return self.__BIK
    
    @BIK.setter
    def BIK(self, value: str|int) -> str:
        if isinstance(value, (str, int)):
            if len(str(value).strip()) == 9:
                self.__BIK = str(value).strip()
            else:
                raise ValueError("Поле BIK должно быть длиной в 9 символов.")
        else:
            raise ValueError("Поле BIK должно быть строкой или числом")

    @property
    def ownership_type(self) -> str:
        return self.__ownership_type
    
    @ownership_type.setter
    def ownership_type(self, value: str) -> str:
        if isinstance(value, str):
            if len(value.strip()) <= 5:
                self.__ownership_type = value.strip()
            else:
                raise ValueError('Поле ownership_type должно быть длиной не более 5 символов.')
        else:
            raise ValueError("Поле ownership_type должно быть строкой")