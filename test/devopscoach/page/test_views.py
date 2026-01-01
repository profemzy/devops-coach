from flask import url_for

from lib.test import ViewTestMixin


class TestPage(ViewTestMixin):
    def test_home_page(self):
        """Home page should show landing page or redirect appropriately."""
        response = self.client.get(url_for("page.home"))

        # 200 = landing page (not logged in)
        # 302 = redirect (either to dashboard if logged in, or to login)
        assert response.status_code in (200, 302)
