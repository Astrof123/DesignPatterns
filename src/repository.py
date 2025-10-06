
class Repository:
    __data= {}

    @property
    def data(self):
        return self.__data
    

    '''
    Ключ для единиц измерения
    '''
    @staticmethod
    def unit_measure_key():
        return "unit_measure"
    

    @staticmethod
    def group_nomenclature_key():
        return "group_nomenclature"
    

    @staticmethod
    def nomenclature_key():
        return "nomenclature"