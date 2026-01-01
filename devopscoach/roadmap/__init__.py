"""Roadmap blueprint for learning roadmaps."""

from flask import Blueprint

roadmap = Blueprint(
    "roadmap",
    __name__,
    url_prefix="/roadmap",
    static_folder="../../static",
    template_folder="../templates",
)

from devopscoach.roadmap import views  # noqa: E402,F401