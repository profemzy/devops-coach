from flask import Blueprint, render_template

page = Blueprint("page", __name__, template_folder="templates")


@page.get("/")
def home():
    """Landing page."""
    return render_template("page/home.html")
