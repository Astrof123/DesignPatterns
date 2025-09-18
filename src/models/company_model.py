
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
        if value.strip() != "":
            self.__name = value.strip()
        else:
            raise ValueError("Поле name не должно быть пустым")


    @property
    def INN(self) -> str:
        return self.__INN
    
    @INN.setter
    def INN(self, value: str) -> str:
        if len(value.strip()) == 12:
            self.__INN = value.strip()
        else:
            raise ValueError("Поле INN должно быть длиной в 12 символов.")


    @property
    def account(self) -> str:
        return self.__account
    
    @account.setter
    def account(self, value: str) -> str:
        if len(value.strip()) == 11:
            self.__account = value.strip()
        else:
            raise ValueError("Поле account должно быть длиной в 11 символов.")


    @property
    def correspondent_account(self) -> str:
        return self.__correspondent_account
    
    @correspondent_account.setter
    def correspondent_account(self, value: str) -> str:
        if len(value.strip()) == 11:
            self.__correspondent_account = value.strip()
        else:
            raise ValueError("Поле correspondent_account должно быть длиной в 11 символов.")


    @property
    def BIK(self) -> str:
        return self.__BIK
    
    @BIK.setter
    def BIK(self, value: str) -> str:
        if len(value.strip()) == 9:
            self.__BIK = value.strip()
        else:
            raise ValueError("Поле BIK должно быть длиной в 9 символов.")


    @property
    def ownership_type(self) -> str:
        return self.__ownership_type
    
    @ownership_type.setter
    def ownership_type(self, value: str) -> str:
        if value in ["Private", "Municipal", "State"]:
            self.__ownership_type = value.strip()
        else:
            raise ValueError('Поле ownership_type должно быть либо "Private", либо "Municipal", либо "State')