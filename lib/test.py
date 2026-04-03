import pytest
from flask import url_for


class ViewTestMixin(object):
    """
    Automatically load in a session and client, this is common for a lot of
    tests that work with views.
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def login(
        self,
        user,
        password="password123",
        next_page=None,
        remember=False,
        follow_redirects=False,
    ):
        """Authenticate the current test client as the given user."""
        data = {
            "username": user.username,
            "password": password,
        }

        if next_page is not None:
            data["next"] = next_page

        if remember:
            data["remember"] = "y"

        return self.client.post(
            url_for("auth.login"),
            data=data,
            follow_redirects=follow_redirects,
        )
