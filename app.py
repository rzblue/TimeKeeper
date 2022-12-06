import logging
import os
from datetime import datetime, timedelta

from bottle import Bottle, template, response, request, redirect, static_file

import loggers
from database import StorageAPI
from helpers import error_page
from models import User

loggers.setup_logger()
logger = logging.getLogger("app")

app = Bottle()

database = StorageAPI(os.getenv("DATABASE_FILE") or "database.sqlite")


@app.route("/")
def home():
    return template("index.html")


@app.route("/sign-in")
def sign_in():
    signed_in_users: list[tuple[str, datetime]] = []
    active_sessions = database.get_active_sessions()
    for session in active_sessions:
        user = database.get_user_by_key(session.user_id)
        signed_in_users.append((user.name, session.start_time))

    return template("sign-in.html", signed_in_users=signed_in_users)


@app.route("/sign-in", method="POST")
def handle_sign_in_out():
    user = database.get_user_by_id_string(request.forms.id_number)
    if user is None:
        return error_page("User not found with that id", "/sign-in")
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


@app.route("/create-user", method="POST")
def handle_create_user():
    user = database.create_user(User(request.forms.full_name, request.forms.id_number))
    if user is None:
        return error_page(f'User already exists with ID "{request.forms.id_number}"')
    redirect("/sign-in")


@app.route("/reports")
def reports_page():
    users = database.get_all_users()
    session_data: list[tuple[str, timedelta]] = []
    for user in users:
        total = timedelta()
        sessions = database.get_completed_time_sessions_for_user(user)
        for session in sessions:
            total += session.total_time or timedelta()
        session_data.append((user.name, total))
    return template("reports.html", session_totals=session_data)


@app.route("/sign-out-all")
def handle_signout_all():
    database.end_all_sessions()
    redirect("/sign-in")
    return ""


@app.route("/static/<filepath>")
def callback(filepath):
    return static_file(filepath, "./static")


app.run(debug=True, reloader=True, host="0.0.0.0")
