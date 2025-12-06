import datetime
import json
from typing import Dict, Optional


class LogFormatter:
    """Форматировщик логов"""
    
    def __init__(self, date_format: str = "%Y-%m-%d %H:%M:%S", 
                 log_format: str = "{timestamp} | {level} | {source} | {message} | {data}"):
        self.date_format = date_format
        self.log_format = log_format
    
    def format(self, level: str, source: str, message: str, data: Optional[Dict] = None) -> str:
        """Форматирует сообщение лога"""
        timestamp = datetime.datetime.now().strftime(self.date_format)
        
        if data:
            try:
                data_str = json.dumps(data, ensure_ascii=False, default=str)
            except:
                data_str = str(data)
        else:
            data_str = "{}"
        
        return self.log_format.format(
            timestamp=timestamp,
            level=level.upper(),
            source=source,
            message=message,
            data=data_str
        )
