class Validator:

    @staticmethod
    def validate(value, variable_type, variable_len=None):
        if value is None:
            raise ValueError("Пустой аргумент")

        if not isinstance(value, variable_type):
            raise ValueError(f"Аргумент должен быть типа {variable_type}")
        
        if len(str(value).strip()) == 0:
            raise ValueError(f"Аргумент не должен быть пустым")

        if variable_len is not None and len(str(value).strip()) != variable_len:
            raise ValueError("Некорректная длина аргумента")
        
        return True