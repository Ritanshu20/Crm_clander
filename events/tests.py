from django.test import TestCase
from django.urls import reverse

class EventsBasicTest(TestCase):
    def test_dashboard_redirects_when_not_logged_in(self):
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
