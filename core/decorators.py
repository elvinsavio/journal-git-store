from flask import redirect, request
from config import Config
from functools import wraps

def is_logged_in(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        is_htmx_request = request.headers.get("HX-Request") == "true"
        login_key = request.cookies.get("_s_key")

        def __redirect_to_login():
            if is_htmx_request:
                resp = redirect("/login")
                resp.headers["HX-Redirect"] = "/login"
                return resp
            else:
                return redirect("/login")

        if not login_key:
            return __redirect_to_login()
        
        if not login_key == Config.HASHED_LOGIN_KEY:
            return __redirect_to_login()
        
        return func(*args, **kwargs)
    
    return wrapper