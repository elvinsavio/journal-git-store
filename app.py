import os

from flask import Flask

from core.router import router

template_dir = os.path.abspath("templates")
static_dir = os.path.abspath("static")

app = Flask(
    __name__, template_folder=template_dir, static_url_path="", static_folder=static_dir
)

if __debug__:
    app.config["TEMPLATES_AUTO_RELOAD"] = True


app.register_blueprint(router)
