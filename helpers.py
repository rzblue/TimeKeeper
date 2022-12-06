from bottle import template


def error_page(message: str, redirect: str = "/"):
    return template("error.html", message=message, redirect=redirect)
