from flask import Flask, render_template
import os

template_dir = os.path.abspath("templates")
static_dir = os.path.abspath("static")

app = Flask(
    __name__, template_folder=template_dir, static_url_path="", static_folder=static_dir
)


@app.route("/")
def home():
    return render_template("login.html")
