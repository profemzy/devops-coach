from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

page = Blueprint("page", __name__, template_folder="templates")


@page.get("/")
def home():
    """Landing page - redirects to dashboard if authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return render_template("page/home.html")
