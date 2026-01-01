from flask import Blueprint

auth = Blueprint("auth", __name__, template_folder="templates")

from devopscoach.auth import forms, views  # noqa: F401, E401, E402
