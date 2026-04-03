from datetime import datetime, timedelta, timezone

from flask import current_app, session
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_login.config import (
    COOKIE_DURATION,
    COOKIE_HTTPONLY,
    COOKIE_NAME,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
)
from flask_login.utils import encode_cookie
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest


def _set_cookie_compat(self, response):
    """Python 3.14-safe replacement for Flask-Login's remember cookie code."""
    config = current_app.config
    cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
    domain = config.get("REMEMBER_COOKIE_DOMAIN")
    path = config.get("REMEMBER_COOKIE_PATH", "/")

    secure = config.get("REMEMBER_COOKIE_SECURE", COOKIE_SECURE)
    httponly = config.get("REMEMBER_COOKIE_HTTPONLY", COOKIE_HTTPONLY)
    samesite = config.get("REMEMBER_COOKIE_SAMESITE", COOKIE_SAMESITE)

    if "_remember_seconds" in session:
        duration = timedelta(seconds=session["_remember_seconds"])
    else:
        duration = config.get("REMEMBER_COOKIE_DURATION", COOKIE_DURATION)

    data = encode_cookie(str(session["_user_id"]))

    if isinstance(duration, int):
        duration = timedelta(seconds=duration)

    try:
        expires = datetime.now(timezone.utc) + duration
    except TypeError as e:
        raise Exception(
            "REMEMBER_COOKIE_DURATION must be a datetime.timedelta,"
            f" instead got: {duration}"
        ) from e

    response.set_cookie(
        cookie_name,
        value=data,
        expires=expires,
        domain=domain,
        path=path,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
    )


bcrypt = Bcrypt()
debug_toolbar = DebugToolbarExtension()
LoginManager._set_cookie = _set_cookie_compat
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
db = SQLAlchemy()
flask_static_digest = FlaskStaticDigest()
