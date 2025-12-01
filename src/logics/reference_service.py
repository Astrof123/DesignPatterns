from src.core.event_type import EventType
from src.core.observe_service import ObserveService
from src.core.prototype import Prototype
from src.dtos.filter_sorting_dto import FilterSortingDto
from src.core.validator import Validator, ArgumentException, OperationException
from src.models.nomenclature_model import NomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.storage_model import StorageModel
from src.models.recipe_model import RecipeModel
from src.models.transaction_model import TransactionModel
from src.models.ingredient_model import IngredientModel
from src.repository import Repository

class ReferenceService:
    """Сервис для работы со справочниками"""
    
    def __init__(self, repository_data: dict):
        Validator.validate(repository_data, dict)
        self.__data = repository_data
    
    @property
    def data(self):
        return self.__data
    
    def _get_reference_data(self, reference_type: str) -> dict:
        """Получить данные справочника по типу"""
        if reference_type not in Repository.get_key_fields(Repository):
            raise ArgumentException(f"Неверный тип справочника: {reference_type}")
        
        return self.data.get(reference_type, {})
    
    def _set_reference_data(self, reference_type: str, data: dict):
        """Установить данные справочника"""
        if reference_type not in Repository.get_key_fields(Repository):
            raise ArgumentException(f"Неверный тип справочника: {reference_type}")
        
        self.data[reference_type] = data
    
    def get_by_id(self, reference_type: str, id: str):
        """Получить элемент справочника по ID"""
        data_dict = self._get_reference_data(reference_type)
        return data_dict.get(id)
    
    def add(self, reference_type: str, item) -> str:
        """Добавить новый элемент в справочник"""
        Validator.validate(item, object)
        
        data_dict = self._get_reference_data(reference_type)
        
        for key, item in data_dict:
            if item.id == id:
                raise ArgumentException(f"Элемент с ID {item.id} уже существует")

        data_dict[item.id] = item
        self._set_reference_data(reference_type, data_dict)
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)

        return item.id
    
    def update(self, reference_type: str, id: str, update_data) -> bool:
        """Обновить элемент справочника с обновлением зависимостей"""
        Validator.validate(id, str)
        Validator.validate(update_data, dict)
        
        data_dict = self._get_reference_data(reference_type)
        
        flag = False
        existing_item = None
        for item in data_dict.values():
            if item.id == id:
                flag = True
                existing_item = item


        if not flag:
            return False

        
        # Обновляем СУЩЕСТВУЮЩИЙ объект, а не заменяем его
        # Это обеспечит автоматическое обновление всех зависимостей

        # Применяем обновления напрямую к существующему объекту
        if reference_type == Repository.nomenclature_key:
            self._update_nomenclature_directly(existing_item, update_data)
        elif reference_type == Repository.unit_measure_key:
            self._update_unit_measurement_directly(existing_item, update_data)
        elif reference_type == Repository.group_nomenclature_key:
            self._update_group_nomenclature_directly(existing_item, update_data)
        elif reference_type == Repository.storage_key:
            self._update_storage_directly(existing_item, update_data)
        else:
            raise ArgumentException(f"Неподдерживаемый тип справочника: {reference_type}")
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)
        
        return True
    
    def delete(self, reference_type: str, id: str) -> bool:
        """Удалить элемент из справочника"""
        Validator.validate(id, str)
        
        ObserveService.create_event(EventType.delete_reference_type_key(), { "reference_type": reference_type, "item_id": id})
        
        data_dict = self._get_reference_data(reference_type)
        
        flag = False
        for key, item in data_dict:
            if item.id == id:
                flag = False

        if not flag:
            return False
        
        del data_dict[id]
        self._set_reference_data(reference_type, data_dict)

        ObserveService.create_event(EventType.change_reference_type_key(), None)
        
        return True
    
    
    def create_item_from_data(self, reference_type: str, data: dict, is_update: bool = False):
        """Создает новый элемент справочника из данных JSON"""
        if reference_type == Repository.nomenclature_key:
            return self._create_nomenclature(data)
        elif reference_type == Repository.unit_measure_key:
            return self._create_unit_measurement(data)
        elif reference_type == Repository.group_nomenclature_key:
            return self._create_group_nomenclature(data)
        elif reference_type == Repository.storage_key:
            return self._create_storage(data)
        else:
            raise ArgumentException(f"Неподдерживаемый тип справочника: {reference_type}")
    
    def _update_nomenclature_directly(self, existing_item: NomenclatureModel, update_data: dict):
        """Обновляет номенклатуру напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']
        
        if 'full_name' in update_data:
            existing_item.full_name = update_data['full_name']
        
        # Обновляем зависимости если переданы
        if 'group_nomenclature_id' in update_data:
            group = self._get_dependency(Repository.group_nomenclature_key, update_data['group_nomenclature_id'])
            existing_item.group_nomenclature = group
        
        if 'unit_measurement_id' in update_data:
            unit = self._get_dependency(Repository.unit_measure_key, update_data['unit_measurement_id'])
            existing_item.unit_measurement = unit
    
    def _update_unit_measurement_directly(self, existing_item: UnitMeasurement, update_data: dict):
        """Обновляет единицу измерения напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']
        
        if 'coefficient' in update_data:
            existing_item.coefficient = update_data['coefficient']
        
        if 'base_unit_id' in update_data:
            base_unit = self._get_dependency(Repository.unit_measure_key, update_data['base_unit_id']) if update_data['base_unit_id'] else None
            existing_item.base_unit = base_unit
    
    def _update_group_nomenclature_directly(self, existing_item: GroupNomenclatureModel, update_data: dict):
        """Обновляет группу номенклатур напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']
    
    def _update_storage_directly(self, existing_item: StorageModel, update_data: dict):
        """Обновляет склад напрямую из данных JSON"""
        if 'name' in update_data:
            existing_item.name = update_data['name']
        
        if 'address' in update_data:
            existing_item.address = update_data['address']


    def _create_new_item(self, reference_type: str, data: dict):
        """Создает новый элемент справочника"""
        if reference_type == Repository.nomenclature_key:
            return self._create_nomenclature(data)
        elif reference_type == Repository.unit_measure_key:
            return self._create_unit_measurement(data)
        elif reference_type == Repository.group_nomenclature_key:
            return self._create_group_nomenclature(data)
        elif reference_type == Repository.storage_key:
            return self._create_storage(data)
        else:
            raise ArgumentException(f"Неподдерживаемый тип справочника: {reference_type}")
    
    def _create_update_object(self, reference_type: str, data: dict):
        """Создает объект для передачи обновлений (не полный объект)"""
        if reference_type == Repository.nomenclature_key:
            return self._create_nomenclature_update(data)
        elif reference_type == Repository.unit_measure_key:
            return self._create_unit_measurement_update(data)
        elif reference_type == Repository.group_nomenclature_key:
            return self._create_group_nomenclature_update(data)
        elif reference_type == Repository.storage_key:
            return self._create_storage_update(data)
        else:
            raise ArgumentException(f"Неподдерживаемый тип справочника: {reference_type}")

    def _create_nomenclature(self, data: dict) -> NomenclatureModel:
        """Создает новую номенклатуру"""
        Validator.validate(data.get('name'), str, field_name="name")
        
        # Получаем зависимости
        group = self._get_dependency(Repository.group_nomenclature_key, data.get('group_nomenclature_id'))
        unit = self._get_dependency(Repository.unit_measure_key, data.get('unit_measurement_id'))
        
        item = NomenclatureModel(
            name=data['name'],
            fullname=data.get('full_name', data['name']),
            group=group,
            unit=unit
        )
        
        # Устанавливаем кастомный ID если передан
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def _create_nomenclature_update(self, data: dict) -> NomenclatureModel:
        """Создает объект номенклатуры для обновления"""
        item = NomenclatureModel("123", "123", None, None)
        
        if 'name' in data:
            item.name = data['name']
        
        if 'full_name' in data:
            item.full_name = data['full_name']
        
        # Устанавливаем зависимости если переданы
        if 'group_nomenclature_id' in data:
            group = self._get_dependency(Repository.group_nomenclature_key, data['group_nomenclature_id'])
            item.group_nomenclature = group
        
        if 'unit_measurement_id' in data:
            unit = self._get_dependency(Repository.unit_measure_key, data['unit_measurement_id'])
            item.unit_measurement = unit
            
        return item
    
    def _create_unit_measurement(self, data: dict) -> UnitMeasurement:
        """Создает новую единицу измерения"""
        Validator.validate(data.get('name'), str, field_name="name")
        Validator.validate(data.get('coefficient'), int, field_name="coefficient")
        
        base_unit = None
        if data.get('base_unit_id'):
            base_unit = self._get_dependency(Repository.unit_measure_key, data['base_unit_id'])
        
        item = UnitMeasurement(
            name=data['name'],
            coefficient=data['coefficient'],
            base_unit=base_unit
        )
        
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def _create_unit_measurement_update(self, data: dict) -> UnitMeasurement:
        """Создает объект единицы измерения для обновления"""
        item = UnitMeasurement("", 1)
        
        if 'name' in data:
            item.name = data['name']
        
        if 'coefficient' in data:
            item.coefficient = data['coefficient']
        
        if 'base_unit_id' in data:
            base_unit = self._get_dependency(Repository.unit_measure_key, data['base_unit_id']) if data['base_unit_id'] else None
            item.base_unit = base_unit
            
        return item
    
    def _create_group_nomenclature(self, data: dict) -> GroupNomenclatureModel:
        """Создает новую группу номенклатур"""
        Validator.validate(data.get('name'), str, field_name="name")
        
        item = GroupNomenclatureModel()
        item.name = data['name']
        
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def _create_group_nomenclature_update(self, data: dict) -> GroupNomenclatureModel:
        """Создает объект группы номенклатур для обновления"""
        item = GroupNomenclatureModel()
        
        if 'name' in data:
            item.name = data['name']
            
        return item
    
    def _create_storage(self, data: dict) -> StorageModel:
        """Создает новый склад"""
        Validator.validate(data.get('name'), str, field_name="name")
        Validator.validate(data.get('address'), str, field_name="address")
        
        item = StorageModel(
            name=data['name'],
            address=data['address']
        )
        
        if 'id' in data:
            item.id = data['id']
            
        return item
    
    def _create_storage_update(self, data: dict) -> StorageModel:
        """Создает объект склада для обновления"""
        item = StorageModel("", "")
        
        if 'name' in data:
            item.name = data['name']
        
        if 'address' in data:
            item.address = data['address']
            
        return item
    
    def _get_dependency(self, reference_type: str, dependency_id: str):
        """Получает зависимый объект по ID"""
        if not dependency_id:
            return None
            
        dependency = self.get_by_id(reference_type, dependency_id)
        if not dependency:
            raise ArgumentException(f"Зависимость {reference_type} с ID {dependency_id} не найдена")
            
        return dependency