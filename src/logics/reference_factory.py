from src.core.observe_service import ObserveService
from src.core.event_type import EventType
from src.logics.group_nomenclature_factory import GroupNomenclatureFactory
from src.logics.nomenclature_factory import NomenclatureFactory
from src.logics.storage_factory import StorageFactory
from src.logics.unit_measurement_factory import UnitMeasurementFactory
from src.core.reference_item_factory import ReferenceItemFactory
from src.core.validator import ArgumentException, OperationException
from src.repository import Repository


class ReferenceFactory:
    """Фабрика для создания фабрик элементов справочников"""
    
    __match = {
        Repository.nomenclature_key: NomenclatureFactory,
        Repository.unit_measure_key: UnitMeasurementFactory,
        Repository.group_nomenclature_key: GroupNomenclatureFactory,
        Repository.storage_key: StorageFactory
    }
    
    def __init__(self, reference_service):
        self.reference_service = reference_service
        self.__factories = {}
        ObserveService.add(self)
        
        # Создаем экземпляры фабрик при инициализации
        for ref_type, factory_class in self.__match.items():
            self.__factories[ref_type] = factory_class(reference_service)
    
    def get_factory(self, reference_type: str) -> ReferenceItemFactory:
        """Получает фабрику для указанного типа справочника"""
        if reference_type not in self.__factories:
            raise ArgumentException(f"Неподдерживаемый тип справочника: {reference_type}")
        
        return self.__factories[reference_type]
    
    def create_item(self, reference_type: str, data: dict):
        """Создает элемент используя соответствующую фабрику"""
        factory = self.get_factory(reference_type)
        return factory.create(data)
    
    def update_item(self, reference_type: str, existing_item, update_data: dict):
        """Обновляет элемент используя соответствующую фабрику"""
        factory = self.get_factory(reference_type)
        factory.update(existing_item, update_data)


    def check_dependencies(self, reference_type: str, item_id: str, reference_service) -> list:
        """Проверяет зависимости элемента используя соответствующую фабрику"""
        factory = self.get_factory(reference_type)
        return factory.check_dependencies(item_id, reference_service)
    

    def handle(self, event: str, params):
        """Проверяет наличие зависимостей перед удалением"""
        if event == EventType.delete_reference_type_key():
            errors = self.check_dependencies(params.reference_type, params.item_id, params.reference_service)
            if errors:
                # Бросаем первую ошибку из списка
                raise OperationException(errors[0])