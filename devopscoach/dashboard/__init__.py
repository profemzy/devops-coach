from flask import Blueprint

dashboard = Blueprint("dashboard", __name__, template_folder="templates")

from devopscoach.dashboard import views  # noqa: F401, E401, E402
