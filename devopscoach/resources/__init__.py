"""Resources blueprint for learning resource management."""

from flask import Blueprint

resources = Blueprint(
    "resources",
    __name__,
    url_prefix="/resources",
    static_folder="../../static",
    template_folder="../templates",
)

from devopscoach.resources import views as views  # noqa: E402
