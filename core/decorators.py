from functools import wraps

from flask import Response, redirect, request

from config import config


def is_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        is_htmx_request = request.headers.get("HX-Request") == "true"
        login_key = request.cookies.get("_s_key")

        def __redirect_to_login_htmx():
            # 204 is common for header-driven redirects; 200 also works.
            return Response("", status=302, headers={"HX-Redirect": "/login"})

        def __redirect_to_login_normal():
            return redirect("/login")

        if not login_key or login_key != config.HASHED_LOGIN_KEY:
            return (
                __redirect_to_login_htmx()
                if is_htmx_request
                else __redirect_to_login_normal()
            )

        return func(*args, **kwargs)

    return wrapper
