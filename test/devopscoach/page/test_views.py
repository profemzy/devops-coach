from flask import url_for

from lib.test import ViewTestMixin


class TestPage(ViewTestMixin):
    def test_home_page(self):
        """Home page should show landing page or redirect appropriately."""
        response = self.client.get(url_for("page.home"))

        assert response.status_code == 200
        assert b"Get Started" in response.data
