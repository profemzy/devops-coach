from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from devopscoach.auth import auth  # Import the Blueprint from __init__.py
from devopscoach.auth.forms import LoginForm, RegistrationForm
from devopscoach.extensions import db
from devopscoach.models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for("page.home"))

    form = LoginForm()
    if form.validate_on_submit():
        # Check if username or email was provided
        user = User.query.filter(
            (User.username == form.username.data)
            | (User.email == form.username.data)
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            next_page = request.args.get("next")
            return (
                redirect(next_page)
                if next_page
                else redirect(url_for("dashboard.index"))
            )
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("page.home"))

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


@auth.route("/logout")
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("page.home"))
