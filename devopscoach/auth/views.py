from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from devopscoach.auth import auth  # Import the Blueprint from __init__.py
from devopscoach.auth.forms import LoginForm, LogoutForm, RegistrationForm
from devopscoach.extensions import db
from devopscoach.models import User


def _is_safe_redirect_target(target: str | None) -> bool:
    """Return True when target is a local redirect destination."""
    if not target:
        return False

    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(target)

    return test_url.scheme in ("", "http", "https") and test_url.netloc in (
        "",
        ref_url.netloc,
    )


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if request.method == "GET":
        form.next.data = request.args.get("next", "")

    if form.validate_on_submit():
        # Check if username or email was provided
        user = User.query.filter(
            (User.username == form.username.data)
            | (User.email == form.username.data)
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login successful!", "success")
            next_page = form.next.data
            return (
                redirect(next_page)
                if _is_safe_redirect_target(next_page)
                else redirect(url_for("dashboard.index"))
            )
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash(
                "Username already exists. Please choose a different one.",
                "danger",
            )
            return render_template("auth/register.html", form=form)

        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash(
                "Email already registered. Please use a different one.",
                "danger",
            )
            return render_template("auth/register.html", form=form)

        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    """Handle user logout."""
    form = LogoutForm()
    if not form.validate_on_submit():
        flash("Unable to log out. Please try again.", "danger")
        return redirect(url_for("dashboard.index"))

    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("page.home"))
