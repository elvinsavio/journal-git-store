from datetime import datetime, timedelta

from flask import Blueprint, Response, render_template, request

from config import Config

from .decorators import is_logged_in
from .model import Status, Todo, _get_current_datetime

router = Blueprint("router", __name__)


@router.route("/")
@is_logged_in
def home():
    weekly_graph = Todo.percentage_weekly()
    daily_graph = Todo().percentage()
    print(daily_graph)
    return render_template(
        "dashboard.html",
        weekly_graph_percentage=weekly_graph["percentage"],
        weekly_graph_count=weekly_graph["count"],
        daily_graph=daily_graph,
    )


@router.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_key = request.form.get("login-key")
        if not login_key:
            return Response("Missing login key", status=200)
        if login_key != Config.LOGIN_KEY:
            return Response("Invalid login key", status=200)
        resp = Response("ok")
        resp.headers["HX-Redirect"] = "/"
        resp.set_cookie(
            "_s_key",
            Config.HASHED_LOGIN_KEY,
            httponly=True,
            samesite="Lax",
            max_age=3600,
        )
        return resp
    if request.method == "GET":
        return render_template("login.html")

    return render_template("404.html")


@router.route("/todo", methods=["GET", "POST"])
@is_logged_in
def todo():
    if request.method == "GET":
        date = request.args.get("_t", None)
        todo = Todo(date=date)
        prev_date = datetime.strptime(todo.date, "%d-%m-%Y") - timedelta(days=1)
        next_date = datetime.strptime(todo.date, "%d-%m-%Y") + timedelta(days=1)
        today = _get_current_datetime()

        is_future: bool = datetime.strptime(todo.date, "%d-%m-%Y").date() > today.date()
        is_present: bool = (
            datetime.strptime(todo.date, "%d-%m-%Y").date() == today.date()
        )
        return render_template(
            "todo.html",
            todos=todo.data,
            today=today,
            date=todo.date,
            next_date=next_date,
            prev_date=prev_date,
            is_future=is_future,
            is_present=is_present,
            percentage=todo.percentage(),
        )

    if request.method == "POST":
        title = request.form.get("title")
        date = request.args.get("_t")

        if not title or not date:
            return render_template("partials/todo/form.html", error="input is required")

        todo = Todo(date=date)
        entry = todo.add(title)
        return render_template("partials/todo/item.html", todo=entry, date=todo.date)

    return render_template("404.html")


@router.route("/todo/<date>/progress", methods=["GET"])
@is_logged_in
def todo_progress(date: str):
    if request.method == "GET":
        percentage = Todo(date=date).percentage()
        return render_template("partials/todo/progress_bar.html", percentage=percentage)
    return render_template("404.html")


@router.route("/todo/<date>/<index>/<method>", methods=["POST", "DELETE"])
@is_logged_in
def todo_date(date: str, index: int, method: str):
    index = int(index)
    if index < 0 or not date or not method:
        raise ValueError("Index, date, and method required")

    if request.method == "POST":
        match method:
            case "completed":
                todo = Todo(date=date).update(index, Status.COMPLETED)
                return render_template("partials/todo/item.html", todo=todo)
            case "postpone":
                todo = Todo(date=date).postpone(index)
                return ""

    if request.method == "DELETE":
        todo = Todo(date=date).update(index, Status.DELETED)
        return render_template("partials/todo/item.html", todo=todo)

    return render_template("404.html")
