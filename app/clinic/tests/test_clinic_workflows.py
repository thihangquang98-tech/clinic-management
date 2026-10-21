from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clinic.forms import (
    PatientForm,
    AppointmentForm,
    PaymentForm,
)
from clinic.models import (
    Patient,
    Doctor,
    Appointment,
    MedicalRecord,
    MedicalService,
    Invoice,
    InvoiceItem,
    Payment,
)

User = get_user_model()


class ClinicWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        receptionist_group, _ = Group.objects.get_or_create(
            name="Receptionist"
        )
        doctor_group, _ = Group.objects.get_or_create(name="Doctor")
        admin_group, _ = Group.objects.get_or_create(name="Admin")

        cls.receptionist = User.objects.create_user(
            username="workflow_receptionist",
            password="TestPassword!2026",
        )
        cls.receptionist.groups.add(receptionist_group)

        cls.doctor_user = User.objects.create_user(
            username="workflow_doctor",
            password="TestPassword!2026",
        )
        cls.doctor_user.groups.add(doctor_group)

        cls.admin_user = User.objects.create_user(
            username="workflow_admin",
            password="TestPassword!2026",
        )
        cls.admin_user.groups.add(admin_group)

        cls.patient = Patient.objects.create(
            full_name="Nguyen Van Test",
            phone="0912345678",
            gender="Nam",
        )
        cls.doctor = Doctor.objects.create(
            full_name="Bac si Test",
            specialty="Noi tong quat",
            phone="0987654321",
            email="doctor.workflow@gmail.com",
        )
        cls.appointment = Appointment.objects.create(
            patient=cls.patient,
            doctor=cls.doctor,
            appointment_time=timezone.now() + timedelta(days=7),
            reason="Kiem tra suc khoe",
            status="scheduled",
        )
        cls.service = MedicalService.objects.create(
            code="TEST001",
            name="Kham tong quat",
            price=Decimal("200000"),
            is_active=True,
        )
        cls.invoice = Invoice.objects.create(
            appointment=cls.appointment,
            notes="Hoa don kiem thu",
        )


class PatientWorkflowTests(ClinicWorkflowTests):
    def test_patient_list_is_accessible_to_receptionist(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("patients"))
        self.assertEqual(response.status_code, 200)

    def test_receptionist_can_create_patient(self):
        self.client.force_login(self.receptionist)
        response = self.client.post(
            reverse("patient_create"),
            {
                "full_name": "Tran Thi New",
                "date_of_birth": "2000-01-01",
                "gender": "Nữ",
                "phone": "0901111222",
                "address": "Thai Nguyen",
            },
        )
        self.assertRedirects(
            response,
            reverse("patients"),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            Patient.objects.filter(phone="0901111222").exists()
        )

    def test_patient_form_rejects_invalid_phone(self):
        form = PatientForm(data={
            "full_name": "Patient Invalid",
            "date_of_birth": "2000-01-01",
            "gender": "Nam",
            "phone": "123",
            "address": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_patient_form_rejects_duplicate_phone(self):
        form = PatientForm(data={
            "full_name": "Patient Duplicate",
            "date_of_birth": "2000-01-01",
            "gender": "Nam",
            "phone": self.patient.phone,
            "address": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)


class AppointmentWorkflowTests(ClinicWorkflowTests):
    def test_appointment_list_is_accessible_to_doctor(self):
        self.client.force_login(self.doctor_user)
        response = self.client.get(reverse("appointments"))
        self.assertEqual(response.status_code, 200)

    def test_appointment_form_rejects_past_time(self):
        past_time = timezone.localtime(
            timezone.now() - timedelta(days=1)
        ).strftime("%Y-%m-%dT%H:%M")

        form = AppointmentForm(data={
            "patient": self.patient.pk,
            "doctor": self.doctor.pk,
            "appointment_time": past_time,
            "reason": "Kiem tra",
            "status": "scheduled",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("appointment_time", form.errors)

    def test_receptionist_can_create_future_appointment(self):
        self.client.force_login(self.receptionist)
        future_time = timezone.localtime(
            timezone.now() + timedelta(days=10)
        ).strftime("%Y-%m-%dT%H:%M")

        response = self.client.post(
            reverse("appointment_create"),
            {
                "patient": self.patient.pk,
                "doctor": self.doctor.pk,
                "appointment_time": future_time,
                "reason": "Kiem tra suc khoe",
                "status": "scheduled",
            },
        )
        self.assertRedirects(
            response,
            reverse("appointments"),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            Appointment.objects.filter(
                patient=self.patient,
                reason="Kiem tra suc khoe",
            ).count(),
            2,
        )


class MedicalRecordWorkflowTests(ClinicWorkflowTests):
    def test_doctor_can_create_medical_record(self):
        self.client.force_login(self.doctor_user)
        response = self.client.post(
            reverse("medical_record_create"),
            {
                "appointment": self.appointment.pk,
                "symptoms": "Dau dau",
                "diagnosis": "Can theo doi",
                "treatment": "Nghi ngoi",
                "notes": "",
            },
        )
        self.assertRedirects(
            response,
            reverse("medical_records"),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            MedicalRecord.objects.filter(
                appointment=self.appointment,
                diagnosis="Can theo doi",
            ).exists()
        )

    def test_receptionist_cannot_create_medical_record(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("medical_record_create"))
        self.assertEqual(response.status_code, 302)


class InvoiceWorkflowTests(ClinicWorkflowTests):
    def test_invoice_generates_unique_code(self):
        another_patient = Patient.objects.create(
            full_name="Another Patient",
            phone="0902222333",
            gender="Nữ",
        )
        another_appointment = Appointment.objects.create(
            patient=another_patient,
            doctor=self.doctor,
            appointment_time=timezone.now() + timedelta(days=14),
            reason="Tai kham",
        )
        another_invoice = Invoice.objects.create(
            appointment=another_appointment,
        )
        self.assertTrue(self.invoice.code)
        self.assertNotEqual(self.invoice.code, another_invoice.code)

    def test_invoice_total_and_remaining_amount(self):
        InvoiceItem.objects.create(
            invoice=self.invoice,
            service=self.service,
            service_name=self.service.name,
            unit_price=self.service.price,
            quantity=2,
        )
        self.assertEqual(self.invoice.total_amount, Decimal("400000"))
        self.assertEqual(self.invoice.paid_amount, Decimal("0"))
        self.assertEqual(self.invoice.remaining_amount, Decimal("400000"))
        self.assertEqual(self.invoice.payment_status, "unpaid")

    def test_payment_form_rejects_amount_above_remaining_balance(self):
        InvoiceItem.objects.create(
            invoice=self.invoice,
            service=self.service,
            service_name=self.service.name,
            unit_price=self.service.price,
            quantity=1,
        )
        form = PaymentForm(
            data={
                "amount": "250000",
                "method": "cash",
                "transaction_code": "",
                "notes": "",
            },
            invoice=self.invoice,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_payment_updates_invoice_balance(self):
        InvoiceItem.objects.create(
            invoice=self.invoice,
            service=self.service,
            service_name=self.service.name,
            unit_price=self.service.price,
            quantity=2,
        )
        Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("150000"),
            method="cash",
            status="success",
        )
        self.assertEqual(self.invoice.paid_amount, Decimal("150000"))
        self.assertEqual(self.invoice.remaining_amount, Decimal("250000"))
        self.assertEqual(self.invoice.payment_status, "partial")


class ReportsWorkflowTests(ClinicWorkflowTests):
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
