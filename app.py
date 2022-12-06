import logging
import os
from datetime import datetime, timedelta

from bottle import Bottle, template, response, request, redirect, static_file

import loggers
from database import StorageAPI
from util import error_page
from models import User, TimeSession

loggers.setup_logger()
logger = logging.getLogger("app")

app = Bottle()

db = StorageAPI(os.getenv("DATABASE_FILE") or "database.sqlite")


@app.route("/")
def home():
    redirect("/sign-in")


@app.route("/sign-in")
def sign_in():
    signed_in_users: list[tuple[str, datetime, int]] = []
    active_sessions = db.get_active_sessions()
    for session in active_sessions:
        user = db.get_user_by_id(session.user_id)
        signed_in_users.append((user.name, session.start_time, session.id))

    return template("sign-in.html", signed_in_users=signed_in_users)


@app.route("/sign-in", method="POST")
def handle_sign_in_out():
    user = db.get_user_by_id_string(request.forms.id_number)
    if user is None:
        return error_page("User not found with that id", "/sign-in")
    session = db.get_latest_active_time_session_for_user(user)
    if session is None:
        db.start_time_session(user)
    else:
        db.end_time_session(session)

    redirect("/sign-in")
    return ""


@app.route("/create-user")
def create_user_page():
    return template("create-user.html")


@app.route("/create-user", method="POST")
def handle_create_user():
    user = db.create_user(User(request.forms.full_name, request.forms.id_number))
    if user is None:
        return error_page(f'User already exists with ID "{request.forms.id_number}"')
    redirect("/sign-in")


@app.route("/reports")
def reports_page():
    users = db.get_all_users()
    session_data: list[tuple[str, timedelta]] = []
    # Loop through list of users
    for user in users:
        total = timedelta()
        # Get the completed sessions for user and iterate through them
        sessions = db.get_completed_time_sessions_for_user(user)
        for session in sessions:
            # add the total time for each session to the total
            total += session.total_time or timedelta()
        # Add the user's total to the list
        session_data.append((user.name, total))
    # Sort by total time, descending
    session_data.sort(reverse=True, key=lambda pair: pair[1].total_seconds())
    return template("reports.html", session_totals=session_data)


@app.route("/sign-out-all")
def handle_signout_all():
    db.end_all_sessions()
    redirect("/sign-in")
    return ""


@app.route("/sign-out/<session_id>")
def sign_out_one(session_id):
    db.end_time_session_by_id(session_id)
    redirect("/sign-in")
    return ""


@app.route("/static/<filepath>")
def callback(filepath):
    return static_file(filepath, "./static")


if __name__ == "__main__":
    app.run(debug=True, reloader=True, host="0.0.0.0")
