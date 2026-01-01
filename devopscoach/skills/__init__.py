from flask import Blueprint

skills = Blueprint("skills", __name__, template_folder="templates")

from devopscoach.skills import forms, views  # noqa: F401, E401, E402
