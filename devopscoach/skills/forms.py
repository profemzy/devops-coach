"""Forms for skills assessment."""

from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


class SkillsAssessmentForm(FlaskForm):
    """Form for assessing user's current skills."""

    # Current Role & Experience
    current_role = StringField(
        "Current Job Title",
        validators=[DataRequired(), Length(min=2, max=100)],
        description="Your current or most recent job title",
    )

    years_of_experience = SelectField(
        "Years of Experience",
        choices=[
            ("0-1", "Less than 1 year"),
            ("1-3", "1-3 years"),
            ("3-5", "3-5 years"),
            ("5-10", "5-10 years"),
            ("10+", "10+ years"),
        ],
        validators=[DataRequired()],
    )

    # Technical Skills
    programming_experience = SelectField(
        "Programming Experience",
        choices=[
            ("none", "No experience"),
            ("basic", "Basic (can write simple scripts)"),
            ("intermediate", "Intermediate (comfortable with code)"),
            ("advanced", "Advanced (professional development)"),
        ],
        validators=[DataRequired()],
    )

    programming_languages = TextAreaField(
        "Programming Languages",
        validators=[Optional(), Length(max=500)],
        description="List languages you know (e.g., Python, JavaScript, Bash)",
    )

    # DevOps Knowledge
    linux_experience = SelectField(
        "Linux/Unix Experience",
        choices=[
            ("none", "No experience"),
            ("basic", "Basic (basic commands)"),
            ("intermediate", "Intermediate (system administration)"),
            ("advanced", "Advanced (performance tuning, kernel work)"),
        ],
        validators=[DataRequired()],
    )

    cloud_experience = SelectField(
        "Cloud Platform Experience",
        choices=[
            ("none", "None"),
            ("aws", "AWS"),
            ("gcp", "Google Cloud Platform"),
            ("azure", "Azure"),
            ("multiple", "Multiple platforms"),
        ],
        validators=[DataRequired()],
    )

    containers_experience = SelectField(
        "Containers (Docker/Kubernetes)",
        choices=[
            ("none", "No experience"),
            ("docker", "Docker only"),
            ("kubernetes", "Kubernetes"),
            ("advanced", "Advanced (production orchestration)"),
        ],
        validators=[DataRequired()],
    )

    cicd_experience = SelectField(
        "CI/CD Experience",
        choices=[
            ("none", "No experience"),
            ("basic", "Basic (used GitHub Actions, etc.)"),
            ("intermediate", "Intermediate (built pipelines)"),
            ("advanced", "Advanced (designed CI/CD systems)"),
        ],
        validators=[DataRequired()],
    )

    # Infrastructure as Code
    iac_experience = SelectField(
        "Infrastructure as Code",
        choices=[
            ("none", "No experience"),
            ("terraform", "Terraform"),
            ("cloudformation", "CloudFormation"),
            ("ansible", "Ansible"),
            ("puppet", "Puppet"),
            ("chef", "Chef"),
            ("multiple", "Multiple tools"),
        ],
        validators=[DataRequired()],
    )

    # Monitoring & Logging
    monitoring_experience = SelectField(
        "Monitoring & Logging",
        choices=[
            ("none", "No experience"),
            ("basic", "Basic (used monitoring tools)"),
            ("intermediate", "Intermediate (set up alerts/dashboards)"),
            ("advanced", "Advanced (built monitoring systems)"),
        ],
        validators=[DataRequired()],
    )

    preferred_learning_style = SelectField(
        "Preferred Learning Style",
        choices=[
            ("visual", "Visual - Videos, diagrams"),
            ("hands-on", "Hands-on - Labs, projects"),
            ("reading", "Reading - Documentation, books"),
            ("interactive", "Interactive - Courses with exercises"),
        ],
        validators=[DataRequired()],
    )

    weekly_learning_hours = SelectField(
        "Weekly Learning Hours",
        choices=[
            ("1-3", "1-3 hours"),
            ("3-5", "3-5 hours"),
            ("5-10", "5-10 hours"),
            ("10+", "10+ hours"),
        ],
        validators=[DataRequired()],
    )

    submit = SubmitField("Analyze My Skills")
