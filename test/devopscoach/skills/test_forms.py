"""Tests for skills assessment forms."""

from devopscoach.skills.forms import SkillsAssessmentForm


class TestSkillsAssessmentForm:
    """Tests for SkillsAssessmentForm."""

    def test_form_valid_with_minimal_data(self, app):
        """Form should be valid with minimal required data."""
        with app.app_context():
            form = SkillsAssessmentForm(
                data={
                    "current_role": "Software Developer",
                    "years_of_experience": "3-5",
                    "programming_experience": "intermediate",
                    "linux_experience": "basic",
                    "cloud_experience": "none",
                    "containers_experience": "none",
                    "cicd_experience": "none",
                    "iac_experience": "none",
                    "monitoring_experience": "none",
                    "preferred_learning_style": "hands-on",
                    "weekly_learning_hours": "5-10",
                }
            )
            assert form.validate()

    def test_form_requires_current_role(self, app):
        """Form should require current_role."""
        with app.app_context():
            form = SkillsAssessmentForm(
                data={
                    "years_of_experience": "3-5",
                    "programming_experience": "intermediate",
                    "linux_experience": "basic",
                    "cloud_experience": "none",
                    "containers_experience": "none",
                    "cicd_experience": "none",
                    "iac_experience": "none",
                    "monitoring_experience": "none",
                    "preferred_learning_style": "hands-on",
                    "weekly_learning_hours": "5-10",
                }
            )
            assert not form.validate()
            assert "current_role" in form.errors

    def test_form_valid_with_all_fields(self, app):
        """Form should be valid with all fields filled."""
        with app.app_context():
            form = SkillsAssessmentForm(
                data={
                    "current_role": "Senior Software Engineer",
                    "years_of_experience": "5-10",
                    "programming_experience": "advanced",
                    "programming_languages": "Python, Go, Bash, JavaScript",
                    "linux_experience": "intermediate",
                    "cloud_experience": "aws",
                    "containers_experience": "kubernetes",
                    "cicd_experience": "intermediate",
                    "iac_experience": "terraform",
                    "monitoring_experience": "intermediate",
                    "preferred_learning_style": "hands-on",
                    "weekly_learning_hours": "10+",
                }
            )
            assert form.validate()

    def test_form_field_choices(self, app):
        """Form fields should accept valid choices."""
        with app.app_context():
            form = SkillsAssessmentForm(
                data={
                    "current_role": "Developer",
                    "years_of_experience": "3-5",
                    "programming_experience": "intermediate",
                    "linux_experience": "basic",
                    "cloud_experience": "aws",
                    "containers_experience": "docker",
                    "cicd_experience": "basic",
                    "iac_experience": "terraform",
                    "monitoring_experience": "basic",
                    "preferred_learning_style": "hands-on",
                    "weekly_learning_hours": "5-10",
                }
            )
            assert form.validate()

    def test_optional_fields_are_optional(self, app):
        """Optional fields should not be required."""
        with app.app_context():
            form = SkillsAssessmentForm(
                data={
                    "current_role": "Developer",
                    "years_of_experience": "3-5",
                    "programming_experience": "intermediate",
                    # programming_languages is optional
                    "linux_experience": "basic",
                    "cloud_experience": "none",
                    "containers_experience": "none",
                    "cicd_experience": "none",
                    "iac_experience": "none",
                    "monitoring_experience": "none",
                    "preferred_learning_style": "hands-on",
                    "weekly_learning_hours": "5-10",
                }
            )
            assert form.validate()
