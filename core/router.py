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

@router.route("/todo", methods=["GET"])
@is_logged_in
def todo():
    return render_template("todo.html")

@router.route("/goals", methods=["GET"])
@is_logged_in
def goals():
    return render_template("goals.html")