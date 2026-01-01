"""Tests for skills blueprint views."""

import uuid

from flask import url_for

from devopscoach.models import User
from lib.test import ViewTestMixin


class TestSkillsAssessment(ViewTestMixin):
    """Tests for skills assessment view."""

    def test_assessment_requires_login(self):
        """Assessment page should redirect to login if not authenticated."""
        # Ensure we're logged out first
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("skills.assessment"))
        # Should redirect to login
        assert response.status_code == 302

    def test_assessment_page_renders(self, session):
        """Assessment page should render for authenticated users."""
        # Create a test user with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        # Login by posting to the login endpoint
        self.client.post(
            url_for("auth.login"),
            data={"username": user.username, "password": "password123"},
        )

        response = self.client.get(url_for("skills.assessment"))
        assert response.status_code == 200
        assert b"Skills Assessment" in response.data

    def test_assessment_form_submission(self, session):
        """Assessment form should create a new assessment."""
        # Create a test user with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        # Login
        self.client.post(
            url_for("auth.login"),
            data={"username": user.username, "password": "password123"},
        )

        # Submit the form
        data = {
            "current_role": "Software Developer",
            "years_of_experience": "3-5",
            "programming_experience": "intermediate",
            "programming_languages": "Python, JavaScript",
            "linux_experience": "basic",
            "cloud_experience": "aws",
            "containers_experience": "docker",
            "cicd_experience": "basic",
            "iac_experience": "none",
            "monitoring_experience": "none",
            "preferred_learning_style": "hands-on",
            "weekly_learning_hours": "5-10",
            "csrf_token": self._get_csrf_token(),
        }

        response = self.client.post(
            url_for("skills.assessment"),
            data=data,
            follow_redirects=False,
        )
        # Should redirect to results
        assert response.status_code == 302

    def _get_csrf_token(self):
        """Helper to get CSRF token from form."""
        response = self.client.get(url_for("skills.assessment"))
        # Extract CSRF token from the page
        # This is a simplified approach - in production you'd parse properly
        import re

        match = re.search(
            rb'name="csrf_token".*?value="([^"]+)"', response.data
        )
        if match:
            return match.group(1).decode("utf-8")
        return ""


class TestSkillsResults(ViewTestMixin):
    """Tests for skills results view."""

    def test_results_requires_login(self):
        """Results page should redirect to login if not authenticated."""
        # Ensure we're logged out first
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("skills.results", assessment_id=1))
        assert response.status_code == 302

    def test_results_page_renders(self, session):
        """Results page should render with recommendations."""
        # Create a test user with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        # Login
        self.client.post(
            url_for("auth.login"),
            data={"username": user.username, "password": "password123"},
        )

        # Create an assessment with recommendations
        from devopscoach.models import SkillAssessment

        assessment = SkillAssessment(
            user_id=user.id,
            assessment_data={
                "current_role": "Developer",
                "years_of_experience": "3-5",
            },
            recommendations={
                "overall_score": 50,
                "readiness_level": "intermediate",
                "strengths": ["Programming experience"],
                "recommended_roles": ["DevOps Engineer", "Platform Engineer"],
                "skill_gaps": [{"skill": "Linux", "priority": "high"}],
                "recommended_roadmap": [
                    {
                        "phase": 1,
                        "title": "Foundations",
                        "duration": "4 weeks",
                        "skills": ["Linux"],
                        "resources": ["Resource 1"],
                    }
                ],
                "certifications": ["AWS Cloud Practitioner"],
                "projects": [
                    {
                        "title": "Sample Project",
                        "description": "A sample project description",
                        "outcome": "What this demonstrates",
                        "level": "Beginner",
                    }
                ],
                "next_steps": ["Step 1"],
            },
        )
        session.add(assessment)
        session.commit()

        response = self.client.get(
            url_for("skills.results", assessment_id=assessment.id)
        )
        assert response.status_code == 200
        assert b"Skills Analysis" in response.data


class TestSkillsHistory(ViewTestMixin):
    """Tests for skills history view."""

    def test_history_requires_login(self):
        """History page should redirect to login if not authenticated."""
        # Ensure we're logged out first
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("skills.history"))
        assert response.status_code == 302

    def test_history_page_renders(self, session):
        """History page should render for authenticated users."""
        # Create a test user with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        # Login
        self.client.post(
            url_for("auth.login"),
            data={"username": user.username, "password": "password123"},
        )

        response = self.client.get(url_for("skills.history"))
        assert response.status_code == 200
        assert b"Assessment History" in response.data
