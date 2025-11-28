from src.core.abstract_model import AbstractModel
from src.core.observe_service import ObserveService
from src.core.event_type import EventType

class print_service(AbstractModel):
    def __init__(self):
        super().__init__()
        ObserveService.add(self)

    def handle(self, event, params):
        super().handle(event, params)

        if event == EventType.convert_to_json:
            print(params)