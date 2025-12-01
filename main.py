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

app = connexion.FlaskApp(__name__)

manager = SettingsManager("settings.json")



start_service = StartService()
start_service.start(manager.settings.first_start)

reference_service = ReferenceService(start_service.data)

balances_manager = BalancesManager(start_service.data, manager.settings.block_period)
start_service.balances = balances_manager.calculation_balances_up_blocking_date()

data_manager = DataManager(start_service.data)

report = Report(start_service.data)

factory = FactoryEntities()

formats = {}

# Проверить доступность REST API
@app.route("/api/accessibility", methods=['GET'])
def formats():
    return "SUCCESS"


# Получить данные в указанном формате
@app.route("/api/data/<data_type>/<format>", methods=['GET'])
def get_data_formatted(data_type: str, format: str):
    
    if data_type not in Repository.get_key_fields(Repository):
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong data_type"}),
            content_type="application/json"
        )
    
    if format not in ResponseFormats.get_all_formats():
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong format"}),
            content_type="application/json"
        )
    
    try:
        data = list(start_service.data[data_type].values())
        
        logic = factory.create(format)
        result = logic().build(format, data)
        
        return Response(
            status=200,
            response=json.dumps(result),
            content_type="application/json"
        )
        
    except Exception as e:
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )


# Получить список доступных моделей данных
@app.route("/api/data/responses/models", methods=['GET'])
def get_models():
    result = [field for field in Repository.get_key_fields(Repository)]

    return Response(
        status=200,
        response=json.dumps(result),
        content_type="application/json"
    )


# Получить список доступных форматов ответа
@app.route("/api/data/responses/formats", methods=['GET'])
def get_formats():
    result = [format for format in ResponseFormats.get_all_formats()]
    return Response(
        status=200,
        response=json.dumps(result),
        content_type="application/json"
    )


@app.route("/api/data/recipes", methods=['GET'])
def get_recipes():
    data = list(start_service.data["recipe"].values())
    
    logic = factory.create("json")
    result = logic().build("json", data)

    return Response(
        status=200,
        response=json.dumps({"result": result}),
        content_type="application/json"
    )


@app.route("/api/data/recipes/<id>", methods=['GET'])
def get_recipe_by_id(id: str):
    data = list(start_service.data["recipe"].values())
    
    recipe = list(filter(lambda recipe: recipe.id == id, data))

    if len(recipe) == 0:
        return Response(
            status=404,
            response=json.dumps({"error": "Recipe not found"}),
            content_type="application/json"
        )        

    logic = factory.create("json")
    result = logic().build("json", recipe)

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

    if data_type not in Repository.get_key_fields(Repository):
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
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    filters = data.get('filters')

    if data_type not in Repository.get_key_fields(Repository):
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong data_type"}),
            content_type="application/json"
        )
    
    if format not in ResponseFormats.get_all_formats():
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong format"}),
            content_type="application/json"
        )
    
    try:
        data = list(start_service.data[data_type].values())
        
        filtersDto = FilterSortingDto(filters, [])

        prototype = Prototype(data)
        
        filtered_prototype = prototype.filter(prototype, filtersDto)


        logic = factory.create(format)
        result = logic().build(format, filtered_prototype.data)
        
        return Response(
            status=200,
            response=json.dumps(result),
            content_type="application/json"
        )
        
    except Exception as e:
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

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong start_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    try:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong end_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    storages = list(start_service.storages.values())
    storage = list(filter(lambda storage: storage.id == storage_id, storages))

    if len(storage) == 0:
        return Response(
            status=404,
            response=json.dumps({"error": "Storage not found"}),
            content_type="application/json"
        )       


    result = report.generateReport(storage[0], start_date, end_date)
    
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
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    filter_model = data.get('filter_model')
    filters = data.get('filters')

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong start_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    try:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong end_date format. Must be year-month-day, for example 2025-12-25."}),
            content_type="application/json"
        )

    storages = list(start_service.storages.values())
    storage = list(filter(lambda storage: storage.id == storage_id, storages))

    if len(storage) == 0:
        return Response(
            status=404,
            response=json.dumps({"error": "Storage not found"}),
            content_type="application/json"
        )       

    
    filtersDto = FilterSortingDto(filters, [])


    result = report.generateReport(storage[0], start_date, end_date, filtersDto, filter_model)
    
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
    return Response(
        status=200,
        response=json.dumps({"block_period": manager.settings.block_period.strftime('%Y-%m-%d')}),
        content_type="application/json"
    )


"""
Меняет текущую дату блокировки
"""
@app.route("/api/block_period", methods=['POST'])
def change_block_date():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    new_block_period = data.get('new_block_period')

    try:
        new_block_period = datetime.datetime.strptime(new_block_period, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong new_block_period format. Must be, for example 2012-04-23."}),
            content_type="application/json"
        )

    manager.settings.block_period = new_block_period
    balances_manager.block_period = new_block_period
    start_service.balances = balances_manager.calculation_balances_up_blocking_date()

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
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    date = data.get('date')

    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            status=400,
            response=json.dumps({"error": "Wrong date format. Must be, for example 2012-04-23."}),
            content_type="application/json"
        )
    balances = balances_manager.calculation_balances_by_date(date)

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

    if data_manager.save_data_to_file():
        return Response(
            status=200,
            response=json.dumps({"success": True}),
            content_type="application/json"
        )
    else:
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
    try:
        item = reference_service.get_by_id(reference_type, id)
        
        if not item:
            return Response(
                status=404,
                response=json.dumps({"error": "Item not found"}),
                content_type="application/json"
            )
        
        logic = factory.create("json")
        result = logic().build("json", [item])
        
        return Response(
            status=200,
            response=json.dumps({"result": result[0] if result else {}}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
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
    try:
        data = request.get_json()
        
        if not data:
            return Response(
                status=400,
                response=json.dumps({"error": "No JSON data received"}),
                content_type="application/json"
            )
        
        # Создаем новый объект
        item = reference_service.create_item_from_data(reference_type, data)
        item_id = reference_service.add(reference_type, item)
        
        return Response(
            status=201,
            response=json.dumps({"id": item_id, "success": True}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
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
    try:
        data = request.get_json()
        
        if not data:
            return Response(
                status=400,
                response=json.dumps({"error": "No JSON data received"}),
                content_type="application/json"
            )
        
        # Обновляем существующий объект напрямую из данных JSON
        success = reference_service.update(reference_type, id, data)
        
        if not success:
            return Response(
                status=404,
                response=json.dumps({"error": "Item not found"}),
                content_type="application/json"
            )
        
        return Response(
            status=200,
            response=json.dumps({"success": True}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
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
    try:
        success = reference_service.delete(reference_type, id)
        
        if not success:
            return Response(
                status=404,
                response=json.dumps({"error": "Item not found"}),
                content_type="application/json"
            )
        
        return Response(
            status=200,
            response=json.dumps({"success": True}),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        return Response(
            status=400,
            response=json.dumps({"error": str(e)}),
            content_type="application/json"
        )
    except Exception as e:
        return Response(
            status=500,
            response=json.dumps({"error": f"Internal server error: {str(e)}"}),
            content_type="application/json"
        )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 8080)