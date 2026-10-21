from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test_receptionist",
            password="TestPassword!2026",
            email="receptionist-test@example.com",
        )
        cls.user.groups.add(
            Group.objects.get_or_create(name="Receptionist")[0]
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "test_receptionist",
                "password": "TestPassword!2026",
            },
        )
        self.assertRedirects(
            response,
            reverse("dashboard"),
            fetch_redirect_response=False,
        )

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "test_receptionist",
                "password": "wrong-password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "không chính xác",
            status_code=200,
        )


class AccessControlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.receptionist = User.objects.create_user(
            username="test_receptionist_access",
            password="TestPassword!2026",
        )
        cls.receptionist.groups.add(
            Group.objects.get_or_create(name="Receptionist")[0]
        )

        cls.doctor = User.objects.create_user(
            username="test_doctor_access",
            password="TestPassword!2026",
        )
        cls.doctor.groups.add(
            Group.objects.get_or_create(name="Doctor")[0]
        )

    def test_anonymous_user_is_redirected_from_dashboard(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_receptionist_can_access_patient_list(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("patients"))
        self.assertEqual(response.status_code, 200)

    def test_receptionist_cannot_access_prescriptions(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("prescriptions"))
        self.assertEqual(response.status_code, 302)

    def test_doctor_can_access_prescriptions(self):
        self.client.force_login(self.doctor)
        response = self.client.get(reverse("prescriptions"))
        self.assertEqual(response.status_code, 200)
