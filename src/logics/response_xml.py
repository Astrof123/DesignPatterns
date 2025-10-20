from src.core.abstract_response import AbstractResponse
from src.core.common import common
import xml.etree.ElementTree as ET

class ResponseXml(AbstractResponse):
    def __init__(self):
        super().__init__()


    def build(self, format: str, data: list):
        super().build(format, data)
            
        root = ET.Element("items")
        
        for item in data:
            item_element = ET.SubElement(root, "item")
            
            # Получаем все публичные атрибуты
            attributes = [attr for attr in dir(item) 
                         if not attr.startswith('_') 
                         and not callable(getattr(item, attr))]
            
            for attr in attributes:
                try:
                    value = getattr(item, attr)
                    field_element = ET.SubElement(item_element, attr)
                    
                    # Обрабатываем вложенные объекты
                    if hasattr(value, '__dict__'):
                        # Для вложенных объектов создаем подэлементы
                        nested_attrs = [nested_attr for nested_attr in dir(value) 
                                      if not nested_attr.startswith('_') 
                                      and not callable(getattr(value, nested_attr))]
                        for nested_attr in nested_attrs:
                            nested_value = getattr(value, nested_attr)
                            if not callable(nested_value):
                                nested_element = ET.SubElement(field_element, nested_attr)
                                nested_element.text = str(nested_value)
                    else:
                        field_element.text = str(value) if value is not None else ""
                        
                except Exception:
                    continue
        
        # Форматируем XML с отступами
        self._indent(root)
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode', method='xml')
    
    def _indent(self, elem, level=0):
        """Добавляет отступы для красивого форматирования XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i