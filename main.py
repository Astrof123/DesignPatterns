import datetime
import json
import time
import connexion
from src.core.validator import ArgumentException
from src.logics.reference_service import ReferenceService
from src.logics.balances_manager import BalancesManager
from src.core.prototype import Prototype
from src.dtos.filter_sorting_dto import FilterSortingDto
from src.core.filter_type import FilterType
from src.core.common import common
from src.data_manager import DataManager
from src.logics.report import Report
from src.logics.factory_entities import FactoryEntities
from src.settings_manager import SettingsManager
from src.core.response_format import ResponseFormats
from flask import jsonify, request, Response
from src.repository import Repository
from src.start_service import StartService

# Импортируем систему логирования
from src.core.logger import Logger

app = connexion.FlaskApp(__name__)

# Настройка логирования
manager = SettingsManager("settings.json")

# Инициализируем логирование с настройками из manager
Logger.configure(
    level=manager.settings.log_level,
    mode=manager.settings.log_mode,
    date_format=manager.settings.log_date_format,
    log_format=manager.settings.log_format,
    log_dir=manager.settings.log_directory
)

Logger.info("Main", "Приложение запускается")
Logger.info("Main", f"Настройки логирования: уровень={manager.settings.log_level}, режим={manager.settings.log_mode}")

# Создаем экземпляры сервисов с логированием
Logger.debug("Main", "Инициализация сервисов")
start_service = StartService()
start_service.start(manager.settings.first_start)
Logger.debug("Main", "StartService инициализирован")

reference_service = ReferenceService(start_service.data)
Logger.debug("Main", "ReferenceService инициализирован")

balances_manager = BalancesManager(start_service.data, manager.settings.block_period)
Logger.info("Main", f"Дата блокировки установлена: {manager.settings.block_period}")
start_service.balances = balances_manager.calculation_balances_up_blocking_date()
Logger.debug("Main", "Балансы рассчитаны до даты блокировки")

data_manager = DataManager(start_service.data)
Logger.debug("Main", "DataManager инициализирован")

report = Report(start_service.data)
Logger.debug("Main", "Report инициализирован")

factory = FactoryEntities()
Logger.info("Main", "Все сервисы успешно инициализированы")

# Проверить доступность REST API
@app.route("/api/accessibility", methods=['GET'])
def formats():
    Logger.debug("API", "GET /api/accessibility - проверка доступности API")
    return "SUCCESS"


# Получить данные в указанном формате
@app.route("/api/data/<data_type>/<format>", methods=['GET'])
def get_data_formatted(data_type: str, format: str):
    Logger.info("API", f"GET /api/data/{data_type}/{format}")
    
    if data_type not in Repository.get_key_fields(Repository):
        Logger.error("API", f"Неверный тип данных: {data_type}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong data_type"}),
            content_type="application/json"
        )
    
    if format not in ResponseFormats.get_all_formats():
        Logger.error("API", f"Неверный формат: {format}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong format"}),
            content_type="application/json"
        )
    
    try:
        data = list(start_service.data[data_type].values())
        Logger.debug("API", f"Получено {len(data)} элементов типа {data_type}")
        
        logic = factory.create(format)
        result = logic().build(format, data)
        
        Logger.info("API", f"Данные типа {data_type} успешно преобразованы в формат {format}")
        return Response(
            status=200,
            response=json.dumps(result),
            content_type="application/json"
        )
        
    except Exception as e:
        Logger.error("API", f"Ошибка при получении данных {data_type}: {str(e)}")
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )


# Получить список доступных моделей данных
@app.route("/api/data/responses/models", methods=['GET'])
def get_models():
    Logger.debug("API", "GET /api/data/responses/models")
    result = [field for field in Repository.get_key_fields(Repository)]

    Logger.debug("API", f"Доступные модели данных: {result}")
    return Response(
        status=200,
        response=json.dumps(result),
        content_type="application/json"
    )


# Получить список доступных форматов ответа
@app.route("/api/data/responses/formats", methods=['GET'])
def get_formats():
    Logger.debug("API", "GET /api/data/responses/formats")
    result = [format for format in ResponseFormats.get_all_formats()]
    
    Logger.debug("API", f"Доступные форматы ответа: {result}")
    return Response(
        status=200,
        response=json.dumps(result),
        content_type="application/json"
    )


@app.route("/api/data/recipes", methods=['GET'])
def get_recipes():
    Logger.debug("API", "GET /api/data/recipes")
    data = list(start_service.data["recipe"].values())
    
    Logger.debug("API", f"Найдено {len(data)} рецептов")
    logic = factory.create("json")
    result = logic().build("json", data)

    return Response(
        status=200,
        response=json.dumps({"result": result}),
        content_type="application/json"
    )


@app.route("/api/data/recipes/<id>", methods=['GET'])
def get_recipe_by_id(id: str):
    Logger.info("API", f"GET /api/data/recipes/{id}")
    data = list(start_service.data["recipe"].values())
    
    recipe = list(filter(lambda recipe: recipe.id == id, data))

    if len(recipe) == 0:
        Logger.warning("API", f"Рецепт с ID {id} не найден")
        return Response(
            status=404,
            response=json.dumps({"error": "Recipe not found"}),
            content_type="application/json"
        )        

    logic = factory.create("json")
    result = logic().build("json", recipe)

    Logger.debug("API", f"Рецепт {id} успешно найден")
    return Response(
        status=200,
        response=json.dumps(result[0]),
        content_type="application/json"
    )


"""
Возвращает поля, по которым можно сделать фильтр, и типы фильтрации
"""
@app.route("/api/filters/<data_type>", methods=['GET'])
def get_filters_by_model(data_type: str):
    Logger.info("API", f"GET /api/filters/{data_type}")

    if data_type not in Repository.get_key_fields(Repository):
        Logger.error("API", f"Неверный тип данных для фильтров: {data_type}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong data_type"}),
            content_type="application/json"
        )
    
    first_elem = list(start_service.data[data_type].values())[0]

    fields_name = common.get_fields_including_internal(first_elem)
    
    result = {
        "filter_field_names": fields_name,
        "filter_types": FilterType.get_all_types()
    }

    Logger.debug("API", f"Фильтры для {data_type}: {len(fields_name)} полей")
    return Response(
        status=200,
        response=json.dumps(result),
        content_type="application/json"
    )


"""
Получить отфильтрованные данные в указанном формате
"""
@app.route("/api/data/<data_type>/<format>", methods=['POST'])
def get_data_filtered(data_type: str, format: str):
    request_data = request.get_json() or {}
    Logger.log_api_request("POST", f"/api/data/{data_type}/{format}", request_data)
    
    if data_type not in Repository.get_key_fields(Repository):
        Logger.error("API", f"Неверный тип данных: {data_type}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong data_type"}),
            content_type="application/json"
        )
    
    if format not in ResponseFormats.get_all_formats():
        Logger.error("API", f"Неверный формат: {format}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong format"}),
            content_type="application/json"
        )
    
    try:
        data = list(start_service.data[data_type].values())
        
        filtersDto = FilterSortingDto(request_data.get('filters', []), [])

        prototype = Prototype(data)
        
        filtered_prototype = prototype.filter(prototype, filtersDto)

        Logger.debug("API", f"Фильтрация {data_type}: {len(data)} -> {len(filtered_prototype.data)} элементов")

        logic = factory.create(format)
        result = logic().build(format, filtered_prototype.data)
        
        Logger.info("API", f"Фильтрованные данные {data_type} успешно преобразованы в формат {format}")
        return Response(
            status=200,
            response=json.dumps(result),
            content_type="application/json"
        )
        
    except Exception as e:
        Logger.error("API", f"Ошибка при фильтрации данных {data_type}: {str(e)}")
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )


"""
Возвращает отчет
"""
@app.route("/api/data/report/<storage_id>/<start_date>/<end_date>", methods=['GET'])
def get_report(storage_id: str, start_date: str, end_date: str):
    Logger.info("API", f"GET /api/data/report/{storage_id}/{start_date}/{end_date}")

    try:
        start_date_parsed = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        Logger.error("API", f"Неверный формат начальной даты: {start_date}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong start_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    try:
        end_date_parsed = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        Logger.error("API", f"Неверный формат конечной даты: {end_date}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong end_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    storages = list(start_service.storages.values())
    storage = list(filter(lambda storage: storage.id == storage_id, storages))

    if len(storage) == 0:
        Logger.warning("API", f"Склад с ID {storage_id} не найден")
        return Response(
            status=404,
            response=json.dumps({"error": "Storage not found"}),
            content_type="application/json"
        )       

    Logger.debug("API", f"Генерация отчета: склад={storage_id}, период={start_date} - {end_date}")
    result = report.generateReport(storage[0], start_date_parsed, end_date_parsed)
    
    Logger.info("API", f"Отчет сгенерирован: {len(result)} строк")
    return Response(
        status=200,
        response=json.dumps({"result": result}),
        content_type="application/json"
    )


"""
Возвращает фильтрованный отчет
"""
@app.route("/api/data/report/<storage_id>/<start_date>/<end_date>", methods=['POST'])
def get_filtered_report(storage_id: str, start_date: str, end_date: str):
    request_data = request.get_json() or {}
    # Логируем POST запрос с данными
    Logger.log_api_request("POST", f"/api/data/report/{storage_id}/{start_date}/{end_date}", request_data)
    
    filter_model = request_data.get('filter_model')
    filters = request_data.get('filters')

    try:
        start_date_parsed = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        Logger.error("API", f"Неверный формат начальной даты: {start_date}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong start_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    try:
        end_date_parsed = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        Logger.error("API", f"Неверный формат конечной даты: {end_date}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong end_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    storages = list(start_service.storages.values())
    storage = list(filter(lambda storage: storage.id == storage_id, storages))

    if len(storage) == 0:
        Logger.warning("API", f"Склад с ID {storage_id} не найден")
        return Response(
            status=404,
            response=json.dumps({"error": "Storage not found"}),
            content_type="application/json"
        )       
    
    filtersDto = FilterSortingDto(filters, [])

    Logger.debug("API", f"Генерация фильтрованного отчета: склад={storage_id}, период={start_date} - {end_date}, модель фильтрации={filter_model}")
    result = report.generateReport(storage[0], start_date_parsed, end_date_parsed, filtersDto, filter_model)
    
    Logger.info("API", f"Фильтрованный отчет сгенерирован: {len(result)} строк")
    return Response(
        status=200,
        response=json.dumps({"result": result}),
        content_type="application/json"
    )


"""
Возвращает текущую дату блокировки
"""
@app.route("/api/block_period", methods=['GET'])
def get_block_date():
    Logger.debug("API", "GET /api/block_period")
    block_date = manager.settings.block_period.strftime('%Y-%m-%d')
    
    Logger.debug("API", f"Текущая дата блокировки: {block_date}")
    return Response(
        status=200,
        response=json.dumps({"block_period": block_date}),
        content_type="application/json"
    )


"""
Меняет текущую дату блокировки
"""
@app.route("/api/block_period", methods=['POST'])
def change_block_date():
    request_data = request.get_json() or {}
    # Логируем POST запрос с данными
    Logger.log_api_request("POST", "/api/block_period", request_data)
    
    new_block_period = request_data.get('new_block_period')

    try:
        new_block_period_parsed = datetime.datetime.strptime(new_block_period, "%Y-%m-%d").date()
    except ValueError:
        Logger.error("API", f"Неверный формат даты блокировки: {new_block_period}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong new_block_period format. Must be, for example 2012-04-23."}),
            content_type="application/json"
        )

    old_date = manager.settings.block_period
    manager.settings.block_period = new_block_period_parsed
    balances_manager.block_period = new_block_period_parsed
    start_service.balances = balances_manager.calculation_balances_up_blocking_date()

    Logger.info("API", f"Дата блокировки изменена: {old_date} -> {new_block_period_parsed}")
    return Response(
        status=200,
        response=json.dumps({"success": True}),
        content_type="application/json"
    )


"""
Возвращает остатки на указанную дату
"""
@app.route("/api/data/balances", methods=['POST'])
def get_balances_by_date():
    request_data = request.get_json() or {}
    # Логируем POST запрос с данными
    Logger.log_api_request("POST", "/api/data/balances", request_data)
    
    date = request_data.get('date')

    try:
        date_parsed = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        Logger.error("API", f"Неверный формат даты: {date}")
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong date format. Must be, for example 2012-04-23."}),
            content_type="application/json"
        )
    
    Logger.debug("API", f"Расчет балансов на дату: {date_parsed}")
    balances = balances_manager.calculation_balances_by_date(date_parsed)

    Logger.info("API", f"Балансы на {date_parsed} рассчитаны: {len(balances)} элементов")
    return Response(
        status=200,
        response=json.dumps({"result": balances}),
        content_type="application/json"
    )


"""
Сохраняет репозиторий в файл
"""
@app.route("/api/data/save", methods=['POST'])
def save_data():
    Logger.info("API", "POST /api/data/save - сохранение данных")

    if data_manager.save_data_to_file():
        Logger.info("API", "Данные успешно сохранены в файл")
        return Response(
            status=200,
            response=json.dumps({"success": True}),
            content_type="application/json"
        )
    else:
        Logger.error("API", "Ошибка при сохранении данных в файл")
        return Response(
            status=500,
            response=json.dumps({"error": "Failed to write to file"}),
            content_type="application/json"
        )


"""
Получить один элемент справочника по ID
"""
@app.route("/api/<reference_type>/<id>", methods=['GET'])
def get_reference_item(reference_type: str, id: str):
    Logger.info("API", f"GET /api/{reference_type}/{id}")
    
    try:
        item = reference_service.get_by_id(reference_type, id)
        
        if not item:
            Logger.warning("API", f"Элемент {reference_type}/{id} не найден")
            return Response(
                status=404,
                response=json.dumps({"error": "Item not found"}),
                content_type="application/json"
            )
        
        logic = factory.create("json")
        result = logic().build("json", [item])
        
        Logger.debug("API", f"Элемент {reference_type}/{id} успешно получен")
        return Response(
            status=200,
            response=json.dumps({"result": result[0] if result else {}}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        Logger.error("API", f"Аргументная ошибка при получении {reference_type}/{id}: {str(e)}")
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
        Logger.error("API", f"Внутренняя ошибка при получении {reference_type}/{id}: {str(e)}")
        return Response(
            status=500,
            response=json.dumps({"error": f"Internal server error: {str(e)}"}),
            content_type="application/json"
        )

"""
Добавить новый элемент в справочник
"""
@app.route("/api/<reference_type>", methods=['PUT'])
def add_reference_item(reference_type: str):
    request_data = request.get_json() or {}
    Logger.log_api_request("PUT", f"/api/{reference_type}", request_data)
    
    try:
        if not request_data:
            Logger.error("API", f"PUT /api/{reference_type} - нет данных в запросе")
            return Response(
                status=400,
                response=json.dumps({"error": "No JSON data received"}),
                content_type="application/json"
            )
        
        # Создаем новый объект
        Logger.debug("API", f"Создание нового элемента для справочника {reference_type}")
        item = reference_service.create_item_from_data(reference_type, request_data)
        item_id = reference_service.add(reference_type, item)
        
        Logger.info("API", f"Новый элемент {reference_type}/{item_id} успешно создан")
        return Response(
            status=201,
            response=json.dumps({"id": item_id, "success": True}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        Logger.error("API", f"Аргументная ошибка при создании элемента в {reference_type}: {str(e)}")
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
        Logger.error("API", f"Внутренняя ошибка при создании элемента в {reference_type}: {str(e)}")
        return Response(
            status=500,
            response=json.dumps({"error": f"Internal server error: {str(e)}"}),
            content_type="application/json"
        )


"""
Изменить элемент справочника
"""
@app.route("/api/<reference_type>/<id>", methods=['PATCH'])
def update_reference_item(reference_type: str, id: str):
    request_data = request.get_json() or {}
    Logger.log_api_request("PATCH", f"/api/{reference_type}/{id}", request_data)
    
    try:
        if not request_data:
            Logger.error("API", f"PATCH /api/{reference_type}/{id} - нет данных в запросе")
            return Response(
                status=400,
                response=json.dumps({"error": "No JSON data received"}),
                content_type="application/json"
            )
        
        # Обновляем существующий объект напрямую из данных JSON
        Logger.debug("API", f"Обновление элемента {reference_type}/{id}")
        success = reference_service.update(reference_type, id, request_data)
        
        if not success:
            Logger.warning("API", f"Элемент {reference_type}/{id} не найден для обновления")
            return Response(
                status=404,
                response=json.dumps({"error": "Item not found"}),
                content_type="application/json"
            )
        
        Logger.info("API", f"Элемент {reference_type}/{id} успешно обновлен")
        return Response(
            status=200,
            response=json.dumps({"success": True}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        Logger.error("API", f"Аргументная ошибка при обновлении {reference_type}/{id}: {str(e)}")
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
        Logger.error("API", f"Внутренняя ошибка при обновлении {reference_type}/{id}: {str(e)}")
        return Response(
            status=500,
            response=json.dumps({"error": f"Internal server error: {str(e)}"}),
            content_type="application/json"
        )

"""
Удалить элемент из справочника
"""
@app.route("/api/<reference_type>/<id>", methods=['DELETE'])
def delete_reference_item(reference_type: str, id: str):
    # Логируем DELETE запрос (особенно важно для PUT/DELETE/PATCH)
    Logger.log_api_request("DELETE", f"/api/{reference_type}/{id}", None)
    
    try:
        Logger.debug("API", f"Удаление элемента {reference_type}/{id}")
        success = reference_service.delete(reference_type, id)
        
        if not success:
            Logger.warning("API", f"Элемент {reference_type}/{id} не найден для удаления")
            return Response(
                status=404,
                response=json.dumps({"error": "Item not found"}),
                content_type="application/json"
            )
        
        Logger.info("API", f"Элемент {reference_type}/{id} успешно удален")
        return Response(
            status=200,
            response=json.dumps({"success": True}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        Logger.error("API", f"Аргументная ошибка при удалении {reference_type}/{id}: {str(e)}")
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
        Logger.error("API", f"Внутренняя ошибка при удалении {reference_type}/{id}: {str(e)}")
        return Response(
            status=500,
            response=json.dumps({"error": f"Internal server error: {str(e)}"}),
            content_type="application/json"
        )


if __name__ == '__main__':
    Logger.info("Main", f"Запуск сервера на 0.0.0.0:8080")
    try:
        app.run(host="0.0.0.0", port=8080)
    except Exception as e:
        Logger.error("Main", f"Ошибка при запуске сервера: {str(e)}")
        raise