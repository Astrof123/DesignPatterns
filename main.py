import json
import connexion
from src.logics.factory_entities import FactoryEntities
from src.settings_manager import SettingsManager
from src.core.response_format import ResponseFormats
from flask import request, Response
from src.repository import Repository
from src.start_service import StartService

app = connexion.FlaskApp(__name__)

start_service = StartService()
start_service.start()
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

    if recipe == 0:
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 8080)