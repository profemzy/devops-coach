"""Tests for resources blueprint views."""

import uuid

from flask import url_for
from flask_login import login_user

from devopscoach.models import LearningResource, User
from lib.test import ViewTestMixin


class TestResourceList(ViewTestMixin):
    """Tests for resource list view."""

    def test_list_requires_login(self):
        """Resource list page should redirect to login if not authenticated."""
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("resources.list_resources"))
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

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("resources.list_resources"))
        assert response.status_code == 200
        assert b"My Learning Resources" in response.data

    def test_list_shows_user_resources(self, session):
        """List page should show only user's own resources."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        resource = LearningResource(
            user_id=user.id,
            title="Docker Mastery",
            resource_type="course",
            url="https://example.com/docker",
            difficulty="intermediate",
            estimated_hours=10,
            tags=["Docker", "Containers"],
        )
        session.add(resource)
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("resources.list_resources"))
        assert response.status_code == 200
        assert b"Docker Mastery" in response.data

    def test_list_filters_by_type(self, session):
        """List page should filter by resource type."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        resource1 = LearningResource(
            user_id=user.id,
            title="Docker Course",
            resource_type="course",
        )
        resource2 = LearningResource(
            user_id=user.id,
            title="Docker Docs",
            resource_type="documentation",
        )
        session.add_all([resource1, resource2])
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("resources.list_resources", type="course"))
        assert response.status_code == 200
        assert b"Docker Course" in response.data
        assert b"Docker Docs" not in response.data

    def test_list_filters_by_status(self, session):
        """List page should filter by completion status."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        resource1 = LearningResource(
            user_id=user.id, title="Completed Course", resource_type="course", is_completed=True
        )
        resource2 = LearningResource(
            user_id=user.id,
            title="Pending Course",
            resource_type="course",
            is_completed=False,
        )
        session.add_all([resource1, resource2])
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(
            url_for("resources.list_resources", status="completed")
        )
        assert response.status_code == 200
        assert b"Completed Course" in response.data
        assert b"Pending Course" not in response.data


class TestResourceCreate(ViewTestMixin):
    """Tests for resource create view."""

    def test_create_requires_login(self):
        """Create page should redirect to login if not authenticated."""
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("resources.create"))
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

        response = self.client.get(url_for("resources.create"))
        assert response.status_code == 200
        assert b"Add Learning Resource" in response.data

    def test_create_form_submission(self, session):
        """Create form should create a new resource."""
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

        response = self.client.get(url_for("resources.create"))
        match = re.search(rb'name="csrf_token".*?value="([^\"]+)"', response.data)
        csrf_token = match.group(1).decode("utf-8") if match else ""

        data = {
            "title": "Kubernetes Fundamentals",
            "description": "Learn K8s from scratch",
            "resource_type": "course",
            "url": "https://example.com/k8s",
            "difficulty": "beginner",
            "estimated_hours": "20",
            "tags": "Kubernetes, K8s, Containers",
            "csrf_token": csrf_token,
            "submit": "Create Resource",
        }

        response = self.client.post(
            url_for("resources.create"),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302

        resource = LearningResource.query.filter_by(
            user_id=user.id,
            title="Kubernetes Fundamentals",
        ).first()
        assert resource is not None
        assert resource.resource_type == "course"
        assert resource.tags == ["Kubernetes", "K8s", "Containers"]


class TestResourceDetail(ViewTestMixin):
    """Tests for resource detail view."""

    def test_detail_requires_login(self):
        """Detail page should redirect to login if not authenticated."""
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("resources.detail", resource_id=1))
        assert response.status_code == 302

    def test_detail_page_renders(self, session):
        """Detail page should render with resource data."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        resource = LearningResource(
            user_id=user.id,
            title="Test Resource",
            resource_type="tutorial",
            description="A test tutorial",
        )
        session.add(resource)
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        response = self.client.get(url_for("resources.detail", resource_id=resource.id))
        assert response.status_code == 200
        assert b"Test Resource" in response.data


class TestResourceToggle(ViewTestMixin):
    """Tests for resource toggle view."""

    def test_toggle_requires_login(self):
        """Toggle should redirect to login if not authenticated."""
        self.client.get(url_for("auth.logout"))
        response = self.client.post(url_for("resources.toggle_complete", resource_id=1))
        assert response.status_code == 302

    def test_toggle_completion(self, session):
        """Toggle should change completion status."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        resource = LearningResource(
            user_id=user.id,
            title="Test Resource",
            resource_type="course",
            is_completed=False,
        )
        session.add(resource)
        session.commit()

        with self.client.application.test_request_context():
            login_user(user)

        # Get CSRF token
        response = self.client.get(url_for("resources.list_resources"))
        import re

        match = re.search(rb'name="csrf_token".*?value="([^\"]+)"', response.data)
        csrf_token = match.group(1).decode("utf-8") if match else ""

        # Toggle to completed
        response = self.client.post(
            url_for("resources.toggle_complete", resource_id=resource.id),
            data={"csrf_token": csrf_token},
            follow_redirects=False,
        )
        assert response.status_code == 302

        session.refresh(resource)
        assert resource.is_completed is True


class TestResourceDelete(ViewTestMixin):
    """Tests for resource delete view."""

    def test_delete_requires_login(self):
        """Delete should redirect to login if not authenticated."""
        self.client.get(url_for("auth.logout"))
        response = self.client.post(url_for("resources.delete", resource_id=1))
        assert response.status_code == 302

    def test_delete_resource(self, session):
        """Delete should remove the resource."""
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        resource = LearningResource(
            user_id=user.id,
            title="Test Resource",
            resource_type="course",
        )
        session.add(resource)
        session.commit()

        resource_id = resource.id

        with self.client.application.test_request_context():
            login_user(user)

        # Get CSRF token
        response = self.client.get(url_for("resources.list_resources"))
        import re

        match = re.search(rb'name="csrf_token".*?value="([^\"]+)"', response.data)
        csrf_token = match.group(1).decode("utf-8") if match else ""

        # Delete
        response = self.client.post(
            url_for("resources.delete", resource_id=resource_id),
            data={"csrf_token": csrf_token},
            follow_redirects=False,
        )
        assert response.status_code == 302

        deleted = LearningResource.query.filter_by(id=resource_id).first()
        assert deleted is None


class TestResourceExplore(ViewTestMixin):
    """Tests for resource explore view."""

    def test_explore_requires_login(self):
        """Explore page should redirect to login if not authenticated."""
        self.client.get(url_for("auth.logout"))
        response = self.client.get(url_for("resources.explore"))
        assert response.status_code == 302

    def test_explore_page_renders(self, session):
        """Explore page should render with recommended resources."""
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

        response = self.client.get(url_for("resources.explore"))
        assert response.status_code == 200
        assert b"Explore DevOps Resources" in response.data
        # Check for some known categories
        assert b"Docker" in response.data or b"Linux" in response.data
