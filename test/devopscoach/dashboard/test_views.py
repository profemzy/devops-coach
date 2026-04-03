"""Tests for dashboard blueprint views."""

import re
import uuid

from flask import url_for

from devopscoach.models import SkillAssessment, User
from lib.test import ViewTestMixin


class TestDashboard(ViewTestMixin):
    """Tests for dashboard view."""

    def test_dashboard_requires_login(self):
        """Dashboard should redirect to login if not authenticated."""
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
        self.login(user)

        response = self.client.get(url_for("dashboard.index"))
        assert response.status_code == 200
        assert b"Welcome back" in response.data
        assert b"Skills Assessed" in response.data

    def test_dashboard_shows_assessment_count(self, session):
        """Dashboard should show the correct assessment count."""
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
        self.login(user)

        # Check dashboard with 0 assessments
        response = self.client.get(url_for("dashboard.index"))
        assert response.status_code == 200
        assert re.search(rb">\s*0\s*<", response.data)

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
        assert re.search(rb">\s*3\s*<", response.data)


class TestAuthViews(ViewTestMixin):
    """Regression tests for auth flows."""

    def _create_user(self, session):
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()
        return user

    def test_login_rejects_external_next_redirect(self, session):
        """Login should ignore unsafe external next URLs."""
        user = self._create_user(session)

        response = self.login(
            user,
            next_page="https://evil.example/phish",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/dashboard/"

    def test_login_redirects_to_safe_next_page(self, session):
        """Login should preserve safe local next URLs."""
        user = self._create_user(session)

        response = self.login(
            user,
            next_page="/skills/assessment",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/skills/assessment"

    def test_login_sets_remember_cookie_when_requested(self, session):
        """Login should set a remember cookie when requested."""
        user = self._create_user(session)

        response = self.login(user, remember=True, follow_redirects=False)

        cookies = response.headers.getlist("Set-Cookie")

        assert response.status_code == 302
        assert any("remember_token=" in cookie for cookie in cookies)

    def test_logout_requires_post(self, session):
        """Logout should not be available over GET."""
        user = self._create_user(session)
        self.login(user)

        response = self.client.get(url_for("auth.logout"))

        assert response.status_code in (404, 405)

    def test_logout_post_clears_session(self, session):
        """Logout should clear the current session."""
        user = self._create_user(session)
        self.login(user)

        response = self.client.post(
            url_for("auth.logout"),
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/"

        protected = self.client.get(url_for("dashboard.index"))
        assert protected.status_code == 302
