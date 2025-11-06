import enum
import json
import os
from datetime import datetime
from typing import Optional

from pytz import timezone

from config import Config


def _get_current_datetime() -> str:
    tz = timezone(Config.TIMEZONE)
    return datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")


def _get_current_date() -> str:
    tz = timezone(Config.TIMEZONE)
    return datetime.now(tz).strftime("%d-%m-%Y")


class Status(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"
    CANCELLED = "canceled"


class Entry:
    def __init__(self, title: str):
        __date = _get_current_date()
        __datetime = _get_current_datetime()
        self.title = title
        self.status = Status.PENDING
        self.date_created = __datetime
        self.date_updated = __datetime
        self.log = ["Task created on " + __date]

    def update_title(self, title: str):
        self.log.append(
            f"Title updated to {title} from {self.title} on {self.date_updated}"
        )
        self.title = title
        self.date_updated = _get_current_datetime()

    def update_status(self, new_status: Status):
        self.status = new_status
        self.date_updated = _get_current_datetime()
        self.log.append(f"Status updated to {new_status.name} on {self.date_updated}")

    def serialize(self) -> dict:
        return {
            "title": self.title,
            "status": self.status.value,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
            "log": self.log,
        }

    @classmethod
    def deserialize(cls, data: dict) -> "Entry":
        entry = cls(data["title"])
        entry.status = Status(data["status"])
        entry.date_updated = data["date_updated"]
        entry.date_created = data["date_created"]
        entry.log = data["log"]
        return entry

    def __repr__(self):
        return f"Entry<title={self.title}, status={self.status.value}>"


class Todo:
    def __init__(self, path: str = "../data/todo.json", date: Optional[str] = None):
        self.file_path = os.path.join(os.path.dirname(__file__), path)
        self.file_path = os.path.abspath(self.file_path)
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Todo file not found at {self.file_path}")
        self.data = []

        if date is None:
            date = _get_current_date()

        self.date = date
        self.__open(date)

    def __open(self, date: str) -> None:
        with open(self.file_path, "r") as f:
            data: dict[str, list[dict]] = json.load(f)
            self.data = [Entry.deserialize(item) for item in data.get(date, [])]

    def __write(self, date: str, data: Entry) -> None:
        """Write data to the JSON file."""
        with open(self.file_path, "r+") as f:
            _data = json.load(f)
            if date not in _data:
                _data[date] = []
            _data[date].append(data.serialize())
            f.seek(0)
            json.dump(_data, f, indent=4)
            f.truncate()
            self.data.append(data)

    def __bulk_write_date(self, date: str, data: list[Entry]) -> None:
        """Write multiple entries to the JSON file."""
        with open(self.file_path, "r+") as f:
            _data = json.load(f)
            _data[date] = [entry.serialize() for entry in data]
            f.seek(0)
            json.dump(_data, f, indent=4)
            f.truncate()
            self.data = data

    def add(self, task: str):
        """Add a task to the todo list for a specific date."""
        date = _get_current_date()
        entry = Entry(task)
        self.__write(date, entry)

    def get(self, index: int) -> Entry:
        """Get a task at a specific index."""
        if index < 0 or index >= len(self.data):
            raise IndexError("Task index out of range")
        return self.data[index]

    def update(
        self, index: int, status: Optional[Status] = None, title: Optional[str] = None
    ) -> None:
        """Update the status of a task at a specific index."""
        if index < 0 or index >= len(self.data):
            raise IndexError("Task index out of range")

        task = self.data[index]

        if title:
            task.update_title(title)
            self.__bulk_write_date(self.date, self.data)
            return

        if status:
            task.update_status(status)
            self.__bulk_write_date(self.date, self.data)
            return

        raise ValueError("Either status or title is required")

    def reorder(self, from_index: int, to_index: int) -> None:
        """Reorder a task from one index to another, matching test expectation."""
        if from_index < 0 or from_index >= len(self.data):
            raise IndexError("From index out of range")
        if to_index < 0 or to_index >= len(self.data):
            raise IndexError("To index out of range")

        self.data[from_index], self.data[to_index] = (
            self.data[to_index],
            self.data[from_index],
        )
        self.__bulk_write_date(self.date, self.data)

    def __len__(self) -> int:
        return len(self.data)
