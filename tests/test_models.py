from datetime import date
import os

from pytest import fixture
import pytest

from core.model import Todo, Entry, Status


def test_entry_init():
    title = "Test Task"
    entry = Entry(title)
    assert entry.title == title
    assert entry.status == Status.PENDING
    assert isinstance(entry.date_created, str)
    assert isinstance(entry.date_updated, str)
    assert len(entry.log) == 1
    assert entry.log[0].startswith("Task created on ")

def test_entry_update_status():
    entry = Entry("Test Task")
    entry.update_status(Status.COMPLETED)
    assert entry.status == Status.COMPLETED
    assert len(entry.log) == 2
    assert entry.log[1].startswith("Status updated to COMPLETED on ")

def test_entry_serialize_deserialize():
    entry = Entry("Test Task")
    entry.update_status(Status.COMPLETED)
    serialized = entry.serialize()
    deserialized = Entry.deserialize(serialized)
    
    assert deserialized.title == entry.title
    assert deserialized.status == entry.status
    assert deserialized.date_created == entry.date_created
    assert deserialized.date_updated == entry.date_updated
    assert deserialized.log == entry.log

def test_entry_postpone():
    entry = Entry("Test Task")
    original_date_updated = entry.date_updated
    entry.postpone()
    assert entry.date_updated != original_date_updated
    assert len(entry.log) == 2
    assert entry.log[1].startswith("Task postponed on ")

def test_entry_serialize_output():
    entry = Entry("Test Task")
    serialized = entry.serialize()
    
    assert serialized["title"] == "Test Task"
    assert serialized["status"] == Status.PENDING.value
    assert isinstance(serialized["date_created"], str)
    assert isinstance(serialized["date_updated"], str)
    assert len(serialized["log"]) == 1
    assert serialized["log"][0].startswith("Task created on ")

def test_entry_deserialize_input():
    data = {
        "title": "Test Task",
        "status": Status.COMPLETED.value,
        "date_created": "01-01-2024 10:00:00",
        "date_updated": "01-01-2024 12:00:00",
        "log": [
            "Task created on 01-01-2024",
            "Status updated to COMPLETED on 01-01-2024 12:00:00"
        ]
    }
    entry = Entry.deserialize(data)
    
    assert entry.title == "Test Task"
    assert entry.status == Status.COMPLETED
    assert entry.date_created == "01-01-2024 10:00:00"
    assert entry.date_updated == "01-01-2024 12:00:00"
    assert entry.log == data["log"]

# @fixture
# def fake_todo_file(tmp_path):
#     todo_file = tmp_path / "todo.json"
#     todo_file.write_text('{}')
#     return str(todo_file)


# def test_todo_init(fake_todo_file):
#     todo = Todo(fake_todo_file)
#     assert todo.file_path.endswith("todo.json")
#     assert os.path.exists(todo.file_path)


# def test_todo_file_not_found():
#    with pytest.raises(FileNotFoundError):
#        Todo("non_existent_file.json")

# def test_todo_add_item(fake_todo_file):
#     todo = Todo(fake_todo_file)
    