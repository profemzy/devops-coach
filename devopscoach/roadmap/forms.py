"""Forms for roadmap management."""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class CreateRoadmapForm(FlaskForm):
    """Form for creating a new learning roadmap."""

    title = StringField(
        "Roadmap Title",
        validators=[DataRequired(), Length(min=3, max=200)],
        description="e.g., DevOps Engineer Learning Path",
    )

    description = TextAreaField(
        "Description (Optional)",
        validators=[Optional(), Length(max=1000)],
        description="Describe your learning goals and timeline",
    )

    target_role = StringField(
        "Target Role",
        validators=[DataRequired(), Length(min=2, max=100)],
        description="e.g., DevOps Engineer, SRE, Platform Engineer",
    )

    timeline_weeks = SelectField(
        "Timeline",
        choices=[
            ("4", "1 month"),
            ("8", "2 months"),
            ("12", "3 months"),
            ("16", "4 months"),
            ("24", "6 months"),
            ("52", "1 year"),
        ],
        validators=[DataRequired()],
        default="12",
    )

    focus_areas = TextAreaField(
        "Focus Areas",
        validators=[Optional(), Length(max=500)],
        description="e.g., Docker, Kubernetes, CI/CD, AWS, Terraform",
    )

    submit = SubmitField("Generate Roadmap")


class UpdateMilestoneForm(FlaskForm):
    """Form for updating milestone progress."""

    status = SelectField(
        "Status",
        choices=[
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
        validators=[DataRequired()],
    )

    notes = TextAreaField(
        "Notes",
        validators=[Optional(), Length(max=1000)],
        description="Add notes about your progress",
    )

    submit = SubmitField("Update Progress")
