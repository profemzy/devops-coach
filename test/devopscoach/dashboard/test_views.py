"""Tests for dashboard blueprint views."""

import uuid

from flask import url_for

from devopscoach.models import SkillAssessment, User
from lib.test import ViewTestMixin


class TestDashboard(ViewTestMixin):
    """Tests for dashboard view."""

    def test_dashboard_requires_login(self):
        """Dashboard should redirect to login if not authenticated."""
        # Ensure we're logged out first
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("dashboard.index"))
        assert response.status_code == 302

    def test_dashboard_page_renders(self, session):
        """Dashboard page should render for authenticated users."""
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

        response = self.client.get(url_for("dashboard.index"))
        assert response.status_code == 200
        assert b"Welcome back" in response.data
        assert b"Skills Assessed" in response.data

    def test_dashboard_shows_assessment_count(self, session):
        """Dashboard should show the correct assessment count."""
        # Ensure clean state
        self.client.get(url_for("auth.logout"))

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

        # Check dashboard with 0 assessments
        response = self.client.get(url_for("dashboard.index"))
        assert response.status_code == 200
        assert b">0<" in response.data

        # Create some assessments
        for i in range(3):
            assessment = SkillAssessment(
                user_id=user.id,
                assessment_data={"role": f"Test Role {i}"},
                recommendations={"overall_score": 50 + i * 10},
            )
            session.add(assessment)
        session.commit()

        # Check dashboard with 3 assessments
        response = self.client.get(url_for("dashboard.index"))
        assert response.status_code == 200
        assert b">3<" in response.data
