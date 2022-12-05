import logging
from datetime import datetime

from bottle import Bottle, template, response, request, redirect

import loggers
from database import StorageAPI

loggers.setup_logger()
logger = logging.getLogger()

app = Bottle()

database = StorageAPI("database.sqlite")


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
    redirect("/sign-in")
    return ""


app.run(reloader=True)
