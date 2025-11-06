import pytest
from flask import Flask
from core.decorators import is_logged_in
from config import Config


@pytest.fixture
def app():
	app = Flask(__name__)

	@app.route("/protected")
	@is_logged_in
	def protected():
		return "secret", 200

	return app


@pytest.fixture
def client(app):
	return app.test_client()


def test_redirects_to_login_when_not_logged_in(client):
	resp = client.get("/protected")

	assert resp.status_code == 302
	assert resp.headers.get("Location", "").endswith("/login")


def test_htmx_sets_hx_redirect_header_when_not_logged_in(client):
	headers = {"HX-Request": "true"}
	resp = client.get("/protected", headers=headers)

	assert resp.status_code == 302
	assert resp.headers.get("HX-Redirect") == "/login"


def test_redirects_when_bad_cookie(client):
	# Set an incorrect login cookie on the test client
	client.set_cookie("_s_key", "wrong_value")
	resp = client.get("/protected")

	assert resp.status_code == 302
	assert resp.headers.get("Location", "").endswith("/login")

def test_redirects_htmx_when_bad_cookie(client):

	headers = {"HX-Request": "true"}
	client.set_cookie("_s_key", "wrong_value")
	resp = client.get("/protected", headers=headers)

	assert resp.headers.get("HX-Redirect") == "/login"
	assert resp.status_code == 302




def test_allows_access_when_logged_in(client):
	# Set the correct hashed login key from Config
	client.set_cookie("_s_key", Config.HASHED_LOGIN_KEY)
	resp = client.get("/protected")

	assert resp.status_code == 200
	assert resp.get_data(as_text=True) == "secret"
	# Set the correct hashed login key from Config

