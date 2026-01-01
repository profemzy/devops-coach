"""Forms for resources blueprint."""

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Optional, URL


class CreateResourceForm(FlaskForm):
    """Form for creating a new learning resource."""

    title = StringField(
        "Resource Title",
        validators=[DataRequired()],
        description="e.g., Docker Mastery - Udemy Course",
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()],
        description="Brief description of what you'll learn",
    )

    resource_type = SelectField(
        "Resource Type",
        choices=[
            ("course", "Course"),
            ("video", "Video"),
            ("article", "Article"),
            ("book", "Book"),
            ("documentation", "Documentation"),
            ("podcast", "Podcast"),
            ("tutorial", "Tutorial"),
            ("certification", "Certification"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )

    url = StringField(
        "URL",
        validators=[Optional(), URL()],
        description="Link to the resource (if applicable)",
    )

    difficulty = SelectField(
        "Difficulty Level",
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        validators=[Optional()],
    )

    estimated_hours = IntegerField(
        "Estimated Hours",
        validators=[Optional()],
        description="How long will this take?",
    )

    tags = StringField(
        "Tags",
        validators=[Optional()],
        description="Comma-separated tags (e.g., Docker, Kubernetes, AWS)",
    )

    submit = StringField("Create Resource")


class EditResourceForm(FlaskForm):
    """Form for editing an existing learning resource."""

    title = StringField(
        "Resource Title",
        validators=[DataRequired()],
        description="e.g., Docker Mastery - Udemy Course",
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()],
        description="Brief description of what you'll learn",
    )

    resource_type = SelectField(
        "Resource Type",
        choices=[
            ("course", "Course"),
            ("video", "Video"),
            ("article", "Article"),
            ("book", "Book"),
            ("documentation", "Documentation"),
            ("podcast", "Podcast"),
            ("tutorial", "Tutorial"),
            ("certification", "Certification"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )

    url = StringField(
        "URL",
        validators=[Optional(), URL()],
        description="Link to the resource (if applicable)",
    )

    difficulty = SelectField(
        "Difficulty Level",
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        validators=[Optional()],
    )

    estimated_hours = IntegerField(
        "Estimated Hours",
        validators=[Optional()],
        description="How long will this take?",
    )

    tags = StringField(
        "Tags",
        validators=[Optional()],
        description="Comma-separated tags (e.g., Docker, Kubernetes, AWS)",
    )

    is_completed = SelectField(
        "Status",
        choices=[
            ("false", "In Progress"),
            ("true", "Completed"),
        ],
        validators=[DataRequired()],
    )

    submit = StringField("Update Resource")
