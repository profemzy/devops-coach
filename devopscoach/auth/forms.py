from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    """Form for user login."""

    username = StringField(
        "Username or Email",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Form for user registration."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Register")
