from src.dtos.filter_dto import FilterDto

class FilterSortingDto:
    __filters = []
    __sorting = []


    {
        "filters": [
            {
                "field_name": "name",
                "value": "Пшеничная мука",
                "type": "LIKE"
            },
            {
                "field_name": "range_name",
                "value": "кг",
                "type": "EQUALS"
            }
        ],
        "sorting": [
            "range_name"
        ]
    }