from .model import Todo
from flask import Blueprint, config, request, redirect, render_template, Response
from config import Config
from .decorators import is_logged_in

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
    raise NotImplementedError("Login logic not implemented yet.")

@router.route("/todo", methods=["GET", "POST", "PUT", "DELETE"])
@is_logged_in
def todo():
    if request.method == "GET":
        date = request.args.get("_t")
        
        if not date:
            return redirect("/")
        
        today_todos = Todo().get_todos_by_date(date)

        return render_template("todo.html", todos=today_todos, date=date)
    if request.method == "POST":
        title = request.form.get("title")
        date = request.form.get("date")
        if not title or not date:
            return Response("Missing title or date", status=400)
        data = {
            "title": title,
            "status": "pending",
            "last_edited": "-",
        }
        Todo().add_todo(date, data)
        resp = Response("ok")
        return resp
    raise NotImplementedError("Todo logic not implemented yet.")

@router.route("/goals", methods=["GET"])
@is_logged_in
def goals():
    return render_template("goals.html")