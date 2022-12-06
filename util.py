import logging
from datetime import timedelta

from bottle import template


def error_page(message: str, redirect: str = "/"):
    logging.getLogger("error_page").error(
        f"Displaying error page with message: '{message}', redirecting to '{redirect}'"
    )
    return template("error.html", message=message, redirect=redirect)


def format_timedelta(time: timedelta) -> str:
    return ""
