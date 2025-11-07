from flask import Blueprint, Response, render_template, request

from config import Config

from .decorators import is_logged_in
from .model import Todo

router = Blueprint("router", __name__)


@router.route("/")
@is_logged_in
def home():
    return render_template("dashboard.html")


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
        todo = Todo()
        return render_template("todo.html", todos=todo.data, date=todo.date)

    if request.method == "POST":
        title = request.form.get("title")

        if not title:
            raise ValueError("Title is required")

        todo = Todo().add(title)
        return render_template("partials/todo_item.html", todo=todo)

    return render_template("404.html")
