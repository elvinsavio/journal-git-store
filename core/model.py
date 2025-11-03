import enum
import os
import json
from datetime import datetime, timedelta
from pytz import timezone
from config import Config

def _get_current_datetime() -> str:
    tz = timezone(Config.TIMEZONE)
    return datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")

def _get_current_date() -> str:
    tz = timezone(Config.TIMEZONE)
    return datetime.now(tz).strftime("%d-%m-%Y")

def _get_next_date() -> str:
    tz = timezone(Config.TIMEZONE)
    next_day = datetime.now(tz).date() + timedelta(days=1)
    return next_day.strftime("%d-%m-%Y")

class Status(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed" 


class Entry:
    def __init__(self, title: str):
        __date = _get_current_date()
        __datetime = _get_current_datetime()
        self.title = title
        self.status = Status.PENDING
        self.date_created = __datetime
        self.date_updated = __datetime
        self.log = [
            "Task created on " + __date
        ]

    def update_status(self, new_status: Status):
        self.status = new_status
        self.date_updated = _get_current_datetime()
        self.log.append(f"Status updated to {new_status.name} on {self.date_updated}")

    def postpone(self):
        self.date_updated = _get_next_date()
        self.log.append(f"Task postponed on {self.date_updated}")

    def serialize(self) -> dict:
        return {
            "title": self.title,
            "status": self.status.value,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
            "log": self.log
        }
    
    @classmethod
    def deserialize(cls, data: dict) -> 'Entry':
        entry = cls(data["title"])
        entry.status = Status(data["status"])
        entry.date_updated = data["date_updated"]
        entry.date_created = data["date_created"]
        entry.log = data["log"]
        return entry

class Todo:
    def __init__(self, path: str = "../data/todo.json"):
        self.file_path = os.path.join(os.path.dirname(__file__), path)
        self.file_path = os.path.abspath(self.file_path)  
        
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Todo file not found at {self.file_path}")
        
        self.file = self.__open()

    def __open(self):
        with open(self.file_path, 'r') as f:
            data = f.read()
            return data
        
    def __write(self, date: str, data: Entry):
        """Write data to the JSON file."""
        with open(self.file_path, 'r+') as f:
            _data = json.load(f)
            if date not in _data:
                _data[date] = []
            
            _data[date].append(data)

            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            
    def __read(self, date: str) -> list[Entry]:
        """Read and parse the JSON file."""
        with open(self.file_path, 'r') as f:
            _data = json.load(f)
            return _data.get(date, [])
        

    def add_task(self, date: str, task: Entry):
        """Add a task to the todo list for a specific date."""
        self.__write(date, task)
    
    def get_tasks(self, date: str):
        """Get tasks for a specific date."""
        return self.__read(date)