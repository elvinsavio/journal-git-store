import enum
import json
import os
from datetime import datetime, timedelta
from typing import Optional

from pytz import timezone

from config import Config


def _get_current_datetime() -> datetime:
    tz = timezone(Config.TIMEZONE)
    return datetime.now(tz)


class Status(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"
    CANCELLED = "canceled"


class Entry:
    def __init__(self, id: int, title: str):
        __datetime = _get_current_datetime()
        self.id: int = id
        self.title: str = title
        self.status: Status = Status.PENDING
        self.date_created: datetime = __datetime
        self.date_updated: datetime = __datetime
        self.log: list[str] = [
            f"Task created on {__datetime.strftime('%d-%m-%Y %H:%M:%S')}"
        ]

    def update_title(self, title: str):
        self.log.append(
            f"Title updated to {title} from {self.title} on {self.date_updated.strftime('%d-%m-%Y, %H:%M:%S')}"
        )
        self.title = title
        self.date_updated = _get_current_datetime()

    def update_status(self, new_status: Status):
        self.status = new_status
        self.date_updated = _get_current_datetime()
        self.log.append(
            f"Status updated to {new_status.name} on {self.date_updated.strftime('%d-%m-%Y, %H:%M:%S')}"
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "date_created": self.date_created.isoformat(),
            "date_updated": self.date_updated.isoformat(),
            "log": self.log,
        }

    @classmethod
    def deserialize(cls, data: dict) -> "Entry":
        entry = cls(data["id"], data["title"])
        entry.id = data["id"]
        entry.status = Status(data["status"])
        entry.date_updated = datetime.fromisoformat(data["date_updated"])
        entry.date_created = datetime.fromisoformat(data["date_created"])
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
            date = _get_current_datetime().strftime("%d-%m-%Y")

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

    def add(self, task: str) -> Entry:
        """Add a task to the todo list"""
        date = self.date
        entry = Entry(len(self), task)
        self.__write(date, entry)
        return entry

    def get(self, index: int) -> Entry:
        """Get a task at a specific index."""
        if index < 0 or index >= len(self.data):
            raise IndexError("Task index out of range")
        return self.data[index]

    def update(
        self, index: int, status: Optional[Status] = None, title: Optional[str] = None
    ) -> Entry:
        """Update the status of a task at a specific index."""
        if index < 0 or index >= len(self.data):
            raise IndexError("Task index out of range")

        task = self.data[index]

        if title:
            task.update_title(title)
            self.__bulk_write_date(self.date, self.data)
            return task

        if status:
            task.update_status(status)
            self.__bulk_write_date(self.date, self.data)
            return task

        raise ValueError("Either status or title is required")

    def reorder(self, from_index: int, to_index: int) -> None:
        """Move a task from one index to another, shifting other tasks accordingly."""
        if from_index < 0 or from_index >= len(self.data):
            raise IndexError("From index out of range")
        if to_index < 0 or to_index >= len(self.data):
            raise IndexError("To index out of range")

        item = self.data.pop(from_index)  # remove the item
        self.data.insert(to_index, item)  # insert it at the new position
        self.__bulk_write_date(self.date, self.data)

    def postpone(self, index: int) -> Entry:
        """Move a task from today to the next day."""
        if index < 0 or index >= len(self.data):
            raise IndexError("Task index out of range")

        with open(self.file_path, "r+") as f:
            data = json.load(f)

        # Current and next day keys
        current_date = datetime.strptime(self.date, "%d-%m-%Y")
        next_day = current_date + timedelta(days=1)
        next_day_str = next_day.strftime("%d-%m-%Y")

        # Get task and remove from today's list
        task = self.data.pop(index)
        task.date_updated = _get_current_datetime()
        task.id = len(Todo(date=next_day_str))
        task.log.append(
            f"Task postponed to {next_day_str} on {task.date_updated.strftime('%d-%m-%Y, %H:%M:%S')}"
        )

        # Update file data
        if next_day_str not in data:
            data[next_day_str] = []

        data[self.date] = [entry.serialize() for entry in self.data]
        data[next_day_str].append(task.serialize())

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

        return task

    def percentage(self):
        """
        Calculate the percentage of tasks by status (completed, pending, deleted)
        for the currently loaded date.
        """
        status_counts = {"completed": 0, "pending": 0, "deleted": 0}
        total = 0

        for task in self.data:
            status = task.status.value.lower()
            if status in status_counts:
                status_counts[status] += 1
                total += 1

        if total == 0:
            return {k: 0.0 for k in status_counts}  # Avoid division by zero

        return {k: round((v / total) * 100, 2) for k, v in status_counts.items()}

    @staticmethod
    def percentage_weekly(path: str = "../data/todo.json") -> dict:
        """
        Static method:
        Computes task status percentages (Completed, Pending, Deleted)
        for the most recent full week (Monday–Sunday).

        Returns:
            dict -> {
                'dates': ['Mon', 'Tue', ...],
                'completed': [...],
                'pending': [...],
                'deleted': [...]
            }
        """
        file_path = os.path.join(os.path.dirname(__file__), path)
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Todo file not found at {file_path}")

        with open(file_path, "r") as f:
            data: dict[str, list[dict]] = json.load(f)

        today_dt = _get_current_datetime()
        monday = today_dt - timedelta(days=today_dt.weekday())

        results = {
            "percentage": {"dates": [], "completed": [], "pending": [], "deleted": []},
            "count": {"dates": [], "completed": [], "pending": [], "deleted": []},
        }

        for i in range(7):
            day = monday + timedelta(days=i)
            day_str = day.strftime("%d-%m-%Y")
            weekday_label = day.strftime("%a")
            entries = data.get(day_str, [])

            results["percentage"]["dates"].append(weekday_label)
            results["count"]["dates"].append(weekday_label)

            if not entries:
                for k in ["completed", "pending", "deleted"]:
                    results["percentage"][k].append(0)
                    results["count"][k].append(0)
                continue

            total = len(entries)
            counts = {"completed": 0, "pending": 0, "deleted": 0}

            for e in entries:
                s = e["status"].lower()
                if s in counts:
                    counts[s] += 1

            for k in counts:
                results["count"][k].append(counts[k])
                results["percentage"][k].append(round((counts[k] / total) * 100, 2))

        return results

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self):
        return f"Todo<date={self.date}, count={len(self)}>"
