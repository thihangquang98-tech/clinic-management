from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ReportsWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        group, _ = Group.objects.get_or_create(name="Receptionist")
        cls.receptionist = User.objects.create_user(
            username="reports_test_user",
            password="TestPassword!2026",
        )
        cls.receptionist.groups.add(group)

    def test_anonymous_user_is_redirected_from_reports(self):
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_receptionist_can_access_reports(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("reports"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("chart_labels", response.context)
        self.assertIn("patient_counts", response.context)
        self.assertIn("appointment_counts", response.context)
        self.assertIn("service_stats", response.context)

    def test_reports_accept_month_and_year_filters(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(
            reverse("reports"),
            {"month": "1", "year": "2026"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["month"], 1)
        self.assertEqual(response.context["year"], 2026)
