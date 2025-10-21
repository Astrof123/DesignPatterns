import connexion
from src.logics.factory_entities import FactoryEntities
from src.settings_manager import SettingsManager
from src.core.response_format import ResponseFormats
from flask import request
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
        return {"error": "Wrong data_type"}, 400
    
    if format not in ResponseFormats.get_all_formats():
        return {"error": "Wrong format"}, 400
    
    try:
        data = list(start_service.data[data_type].values())
        
        logic = factory.create(format)
        result = logic().build(format, data)
        
        return {
            "result": result
        }
        
    except Exception as e:
        return {"error": str(e)}, 400


# Получить список доступных моделей данных
@app.route("/api/data/responses/models", methods=['GET'])
def get_models():
    return {"result": [field for field in Repository.get_key_fields(Repository)]}


# Получить список доступных форматов ответа
@app.route("/api/data/responses/formats", methods=['GET'])
def get_formats():
    return {"result": [format for format in ResponseFormats.get_all_formats()]}



if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 8080)