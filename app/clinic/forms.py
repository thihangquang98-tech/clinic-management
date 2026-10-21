
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    Patient,
    Doctor,
    Appointment,
    MedicalRecord,
    MedicalService,
    Employee,
)

User = get_user_model()

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "full_name",
            "date_of_birth",
            "gender",
            "phone",
            "address",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Họ và tên bệnh nhân",
            }),
            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nhập 10 chữ số, ví dụ 0912345678",
                "maxlength": "10",
                "inputmode": "numeric",
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Địa chỉ",
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if not re.fullmatch(r"0[0-9]{9}", phone):
            raise forms.ValidationError(
                "Số điện thoại phải bắt đầu bằng 0 và gồm đúng 10 chữ số."
            )

        duplicates = Patient.objects.filter(phone=phone)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise forms.ValidationError(
                "Số điện thoại này đã được sử dụng bởi bệnh nhân khác."
            )

        return phone


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["full_name", "specialty", "phone", "email"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Họ và tên bác sĩ",
            }),
            "specialty": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Chuyên khoa",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nhập 10 chữ số, ví dụ 0912345678",
                "maxlength": "10",
                "inputmode": "numeric",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "example@gmail.com",
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if not re.fullmatch(r"0[0-9]{9}", phone):
            raise forms.ValidationError(
                "Số điện thoại phải bắt đầu bằng 0 và gồm đúng 10 chữ số."
            )

        duplicates = Doctor.objects.filter(phone=phone)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise forms.ValidationError(
                "Số điện thoại này đã được sử dụng bởi bác sĩ khác."
            )

        return phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip()

        if not re.fullmatch(
            r"[A-Za-z0-9._%+-]+@gmail\.com",
            email,
            flags=re.IGNORECASE,
        ):
            raise forms.ValidationError(
                "Email phải có định dạng Gmail, ví dụ example@gmail.com."
            )

        return email


class AppointmentForm(forms.ModelForm):
    appointment_time = forms.DateTimeField(
        label="Thời gian khám",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "class": "form-control",
                "type": "datetime-local",
            },
        ),
    )

    class Meta:
        model = Appointment
        fields = [
            "patient",
            "doctor",
            "appointment_time",
            "reason",
            "status",
        ]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-control"}),
            "doctor": forms.Select(attrs={"class": "form-control"}),
            "reason": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Lý do khám",
            }),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data["appointment_time"]

        if timezone.is_naive(appointment_time):
            appointment_time = timezone.make_aware(
                appointment_time,
                timezone.get_current_timezone(),
            )

        if appointment_time <= timezone.now():
            raise forms.ValidationError(
                "Lịch hẹn phải ở thời điểm tương lai. "
                "Vui lòng chọn ngày giờ sau thời điểm hiện tại."
            )

        return appointment_time


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            "appointment",
            "symptoms",
            "diagnosis",
            "treatment",
            "notes",
        ]
        widgets = {
            "appointment": forms.Select(attrs={
                "class": "form-control",
            }),
            "symptoms": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Mô tả triệu chứng của bệnh nhân",
            }),
            "diagnosis": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Nhập chẩn đoán của bác sĩ",
            }),
            "treatment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Phương pháp điều trị, hướng dẫn chăm sóc",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Ghi chú bổ sung",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["appointment"].queryset = (
            Appointment.objects.select_related("patient", "doctor")
            .order_by("-appointment_time")
        )
        self.fields["appointment"].label_from_instance = (
            lambda obj: (
                f"{obj.patient.full_name} - "
                f"{obj.doctor.full_name} - "
                f"{obj.appointment_time:%d/%m/%Y %H:%M}"
            )
        )


class MedicalServiceForm(forms.ModelForm):
    class Meta:
        model = MedicalService
        fields = ["code", "name", "description", "price", "is_active"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "1000"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
    def clean_code(self):
        code = self.cleaned_data["code"].strip()

        existing = MedicalService.objects.filter(code__iexact=code)

        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise forms.ValidationError(
                "Mã dịch vụ đã tồn tại. Vui lòng nhập mã khác."
            )

        return code

from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Invoice, InvoiceItem, Payment, Appointment, MedicalService


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["appointment", "notes"]
        widgets = {
            "appointment": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ghi chú hóa đơn",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["appointment"].queryset = (
            Appointment.objects.select_related("patient", "doctor")
            .order_by("-appointment_time")
        )
        self.fields["appointment"].label_from_instance = lambda obj: (
            f"{obj.patient.full_name} - {obj.doctor.full_name} - "
            f"{obj.appointment_time:%d/%m/%Y %H:%M}"
        )


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["service", "quantity"]
        widgets = {
            "service": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "step": 1,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = MedicalService.objects.filter(
            is_active=True
        ).order_by("name")


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "method", "transaction_code", "notes"]
        widgets = {
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "step": 1,
                "placeholder": "Số tiền thanh toán (VNĐ)",
            }),
            "method": forms.Select(attrs={"class": "form-control"}),
            "transaction_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Mã giao dịch (nếu có)",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Ghi chú thanh toán",
            }),
        }

    def __init__(self, *args, invoice=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoice = invoice

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= Decimal("0"):
            raise ValidationError("Số tiền thanh toán phải lớn hơn 0.")

        if self.invoice is not None:
            remaining = self.invoice.remaining_amount
            if amount > remaining:
                raise ValidationError(
                    f"Số tiền vượt số dư còn phải trả: {remaining:,.0f} VNĐ."
                )

        return amount
class EmployeeForm(forms.ModelForm):
    username = forms.CharField(
        label="Tên đăng nhập",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "username",
        }),
    )

    password = forms.CharField(
        label="Mật khẩu",
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "new-password",
        }),
        help_text="Bắt buộc khi tạo mới; khi sửa có thể để trống.",
    )

    class Meta:
        model = Employee
        fields = [
            "employee_code",
            "full_name",
            "phone",
            "email",
            "position",
            "start_date",
        ]
        widgets = {
            "employee_code": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": "10",
                "inputmode": "numeric",
                "placeholder": "Ví dụ: 0912345678",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
            }),
            "position": forms.Select(attrs={
                "class": "form-control",
            }),
            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["username"].initial = self.instance.user.get_username()
            self.fields["password"].help_text = (
                "Để trống nếu không muốn đổi mật khẩu."
            )
        else:
            self.fields["password"].required = True

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if not re.fullmatch(r"0[0-9]{9}", phone):
            raise forms.ValidationError(
                "Số điện thoại phải gồm đúng 10 chữ số và bắt đầu bằng 0."
            )

        return phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        duplicates = Employee.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise forms.ValidationError(
                "Email này đã được sử dụng bởi nhân viên khác."
            )

        return email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        duplicates = User.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.user_id)

        if duplicates.exists():
            raise forms.ValidationError(
                "Tên đăng nhập này đã được sử dụng."
            )

        return username

    def clean(self):
        cleaned_data = super().clean()
        position = cleaned_data.get("position")

        if position and not Group.objects.filter(name=position).exists():
            self.add_error(
                "position",
                "Nhóm quyền chưa được cấu hình trong hệ thống.",
            )

        return cleaned_data

from .models import Prescription, PrescriptionItem


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["medical_record", "instructions"]
        widgets = {
            "medical_record": forms.Select(attrs={
                "class": "form-control",
            }),
            "instructions": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Lời dặn của bác sĩ",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["medical_record"].queryset = (
            MedicalRecord.objects.select_related(
                "appointment",
                "appointment__patient",
                "appointment__doctor",
            ).order_by("-id")
        )
        self.fields["medical_record"].label_from_instance = (
            lambda record: (
                f"{record.appointment.patient.full_name} - "
                f"{record.appointment.doctor.full_name} - "
                f"Hồ sơ #{record.pk}"
            )
        )


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = [
            "medicine_name",
            "strength",
            "dosage",
            "frequency",
            "duration_days",
            "quantity",
            "usage_instructions",
        ]
        widgets = {
            "medicine_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Tên thuốc",
            }),
            "strength": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Hàm lượng",
            }),
            "dosage": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Liều mỗi lần theo chỉ định",
            }),
            "frequency": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Số lần dùng theo chỉ định",
            }),
            "duration_days": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "usage_instructions": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Cách dùng và lưu ý",
            }),
        }
