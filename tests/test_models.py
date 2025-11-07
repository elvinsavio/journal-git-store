import os

import pytest
from pytest import fixture

from core.model import Entry, Status, Todo


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


def test_entry_update_title():
    entry = Entry("Test Task")
    entry.update_title("Testing")
    assert entry.title == "Testing"
    assert len(entry.log) == 2
    assert entry.log[1].startswith("Title updated to ")


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
            "Status updated to COMPLETED on 01-01-2024 12:00:00",
        ],
    }
    entry = Entry.deserialize(data)

    assert entry.title == "Test Task"
    assert entry.status == Status.COMPLETED
    assert entry.date_created == "01-01-2024 10:00:00"
    assert entry.date_updated == "01-01-2024 12:00:00"
    assert entry.log == data["log"]


@fixture
def fake_todo_file(tmp_path):
    todo_file = tmp_path / "todo.json"
    todo_file.write_text("{}")
    return str(todo_file)


@fixture
def fake_todo_with_data(tmp_path):
    todo_file = tmp_path / "todo.json"
    todo_file.write_text("{}")
    todo = Todo(str(todo_file))
    todo.add("task1")
    todo.add("task2")
    todo.add("task3")
    return str(todo_file)


def test_todo_init(fake_todo_file):
    todo = Todo(fake_todo_file)
    assert todo.file_path.endswith("todo.json")
    assert os.path.exists(todo.file_path)


def test_todo_file_not_found():
    with pytest.raises(FileNotFoundError):
        Todo("non_existent_file.json")


def test_todo_add_item(fake_todo_file):
    todo = Todo(fake_todo_file)
    assert todo.data == []
    todo.add("New Task")
    assert len(todo) == 1
    todo.add("Another Task")
    assert len(todo) == 2


def test_todo_get_item(fake_todo_with_data):
    todo = Todo(fake_todo_with_data)
    assert len(todo) == 3
    entry = todo.get(1)
    assert entry.title == "task2"
    assert entry.status == Status.PENDING

    entry = todo.get(0)
    assert entry.title == "task1"
    assert entry.status == Status.PENDING


def test_todo_get_out_of_range(fake_todo_with_data):
    with pytest.raises(IndexError):
        Todo(fake_todo_with_data).get(90)


def test_dodo_update_item_title(fake_todo_with_data):
    todo = Todo(fake_todo_with_data)
    todo.update(0, title="new title")
    entry = todo.get(0)
    assert entry.title == "new title"
    assert len(entry.log) == 2

    todo.update(2, title="even new")
    entry = todo.get(2)
    assert entry.title == "even new"
    assert len(entry.log) == 2


def test_todo_update_item_status(fake_todo_with_data):
    todo = Todo(fake_todo_with_data)
    todo.update(0, status=Status.COMPLETED)
    entry = todo.get(0)
    assert entry.status == Status.COMPLETED
    assert len(entry.log) == 2

    todo.update(2, status=Status.COMPLETED)
    entry = todo.get(2)
    assert entry.status == Status.COMPLETED
    assert len(entry.log) == 2

    todo.update(2, status=Status.DELETED)
    entry = todo.get(2)
    assert entry.status == Status.DELETED
    assert len(entry.log) == 3

    todo.update(2, status=Status.CANCELLED)
    entry = todo.get(2)
    assert entry.status == Status.CANCELLED
    assert len(entry.log) == 4


def test_todo_reorder_basic(fake_todo_with_data):
    """Reorders tasks by moving one to a new position."""
    todo = Todo(fake_todo_with_data)

    # Initial order: task1, task2, task3
    todo.reorder(0, 2)
    # Expected order: task2, task3, task1
    assert todo.get(0).title == "task2"
    assert todo.get(1).title == "task3"
    assert todo.get(2).title == "task1"

    # Move task2 (index 0) to index 1
    todo.reorder(0, 1)
    # Expected order: task3, task2, task1
    assert todo.get(0).title == "task3"
    assert todo.get(1).title == "task2"
    assert todo.get(2).title == "task1"
