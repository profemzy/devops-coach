"""Tests for roadmap blueprint views."""

import uuid
from datetime import timedelta

from flask import url_for
from flask_login import login_user

from devopscoach.models import CustomRoadmap, SkillAssessment, User
from devopscoach.utils.datetime import utc_now
from lib.test import ViewTestMixin


class TestRoadmapList(ViewTestMixin):
    """Tests for roadmap list view."""

    def test_list_requires_login(self):
        """Roadmap list page should redirect to login if not authenticated."""
        response = self.client.get(url_for("roadmap.list_roadmaps"))
        assert response.status_code == 302

    def test_list_page_renders(self, session):
        """List page should render for authenticated users."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        # Use the test client's request context to login
        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("roadmap.list_roadmaps"))
        assert response.status_code == 200
        assert b"My Learning Roadmaps" in response.data

    def test_list_shows_user_roadmaps(self, session):
        """List page should show only user's own roadmaps."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        roadmap = CustomRoadmap(
            user_id=user.id,
            title="My DevOps Roadmap",
            description="Learning path to DevOps",
            roadmap_data={
                "target_role": "DevOps Engineer",
                "timeline_weeks": 12,
                "milestones": [],
            },
        )
        session.add(roadmap)
        session.commit()

        # Use the test client's request context to login
        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("roadmap.list_roadmaps"))
        assert response.status_code == 200
        assert b"My DevOps Roadmap" in response.data


class TestRoadmapCreate(ViewTestMixin):
    """Tests for roadmap create view."""

    def test_create_requires_login(self):
        """Create page should redirect to login if not authenticated."""
        response = self.client.get(url_for("roadmap.create"))
        assert response.status_code == 302

    def test_create_page_renders(self, session):
        """Create page should render for authenticated users."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("roadmap.create"))
        assert response.status_code == 200
        assert b"Create Your Learning Roadmap" in response.data

    def test_create_form_submission(self, session):
        """Create form should create a new roadmap."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        import re

        response = self.client.get(url_for("roadmap.create"))
        match = re.search(
            rb'name="csrf_token".*?value="([^"]+)"', response.data
        )
        csrf_token = match.group(1).decode("utf-8") if match else ""

        data = {
            "title": "DevOps Engineer Path",
            "description": "My journey to DevOps",
            "target_role": "DevOps Engineer",
            "timeline_weeks": "12",
            "focus_areas": "Docker, Kubernetes, AWS",
            "csrf_token": csrf_token,
        }

        response = self.client.post(
            url_for("roadmap.create"),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302

        roadmap = CustomRoadmap.query.filter_by(
            user_id=user.id,
            title="DevOps Engineer Path",
        ).first()
        assert roadmap is not None
        assert roadmap.roadmap_data["target_role"] == "DevOps Engineer"

    def test_create_prefills_from_latest_assessment(self, session):
        """Create page should use the newest assessment for defaults."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        older = SkillAssessment(
            user_id=user.id,
            assessment_date=utc_now() - timedelta(days=2),
            assessment_data={"current_role": "Developer"},
            recommendations={
                "recommended_roles": ["Platform Engineer"],
                "skill_gaps": [{"skill": "Linux"}],
            },
        )
        newer = SkillAssessment(
            user_id=user.id,
            assessment_date=utc_now(),
            assessment_data={"current_role": "Developer"},
            recommendations={
                "recommended_roles": ["Site Reliability Engineer (SRE)"],
                "skill_gaps": [{"skill": "Kubernetes"}],
            },
        )
        session.add_all([older, newer])
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("roadmap.create"))

        assert response.status_code == 200
        assert b"My Path to Site Reliability Engineer (SRE)" in response.data
        assert b"Kubernetes" in response.data


class TestRoadmapDetail(ViewTestMixin):
    """Tests for roadmap detail view."""

    def test_detail_requires_login(self):
        """Detail page should redirect to login if not authenticated."""
        response = self.client.get(url_for("roadmap.detail", roadmap_id=1))
        assert response.status_code == 302

    def test_detail_page_renders(self, session):
        """Detail page should render with roadmap data."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        roadmap = CustomRoadmap(
            user_id=user.id,
            title="Test Roadmap",
            roadmap_data={
                "target_role": "DevOps Engineer",
                "timeline_weeks": 12,
                "milestones": [
                    {
                        "phase": 1,
                        "title": "Foundations",
                        "duration_weeks": 4,
                        "skills": ["Linux", "Git"],
                        "status": "not_started",
                    },
                ],
            },
        )
        session.add(roadmap)
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(
            url_for("roadmap.detail", roadmap_id=roadmap.id)
        )
        assert response.status_code == 200
        assert b"Test Roadmap" in response.data

    def test_detail_shows_progress(self, session):
        """Detail page should calculate and display progress."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        roadmap = CustomRoadmap(
            user_id=user.id,
            title="Test Roadmap",
            roadmap_data={
                "target_role": "DevOps Engineer",
                "timeline_weeks": 12,
                "milestones": [
                    {
                        "phase": 1,
                        "title": "Foundations",
                        "duration_weeks": 4,
                        "skills": ["Linux"],
                        "status": "completed",
                    },
                    {
                        "phase": 2,
                        "title": "Containers",
                        "duration_weeks": 4,
                        "skills": ["Docker"],
                        "status": "in_progress",
                    },
                    {
                        "phase": 3,
                        "title": "CI/CD",
                        "duration_weeks": 4,
                        "skills": ["GitHub Actions"],
                        "status": "not_started",
                    },
                ],
            },
        )
        session.add(roadmap)
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(
            url_for("roadmap.detail", roadmap_id=roadmap.id)
        )
        assert response.status_code == 200
        # Check for progress indicator - either percentage or milestone count
        assert b"1/3" in response.data or b"50%" in response.data
