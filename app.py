import logging
import os
from datetime import datetime

from bottle import Bottle, template, response, request, redirect, static_file

import loggers
from database import StorageAPI

loggers.setup_logger()
logger = logging.getLogger("app")

app = Bottle()

database = StorageAPI(os.getenv("DATABASE_FILE") or "database.sqlite")


@app.route("/")
def home():
    return template("views/index.html")


@app.route("/sign-in")
def sign_in():
    signed_in_users: list[tuple[str, datetime]] = []
    active_sessions = database.get_active_sessions()
    for session in active_sessions:
        user = database.get_user_by_key(session.user_id)
        signed_in_users.append((user.name, session.start_time))

    return template("views/sign-in.html", signed_in_users=signed_in_users)


@app.route("/sign-in", method="POST")
def handle_sign_in():
    user = database.get_user_by_id_string(request.forms.id_number)
    if user is None:
        return template(
            "error.html", message="User not found with that id", redirect="/sign-in"
        )
    session = database.get_latest_active_time_session_for_user(user)
    if session is None:
        database.start_time_session(user)
    else:
        database.end_time_session(session)

    redirect("/sign-in")
    return ""


@app.route("/create-user")
def create_user_page():
    return template("create-user.html")


@app.route("/static/<filepath>")
def callback(filepath):
    return static_file(filepath, "./static")


app.run(debug=True, reloader=True, host="0.0.0.0")
