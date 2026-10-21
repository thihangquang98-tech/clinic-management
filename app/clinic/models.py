
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

class Patient(models.Model):
    GENDER_CHOICES = [
        ("Nam", "Nam"),
        ("Nữ", "Nữ"),
        ("Khác", "Khác"),
    ]

    full_name = models.CharField("Họ và tên", max_length=150)
    date_of_birth = models.DateField(
        "Ngày sinh",
        null=True,
        blank=True,
    )
    gender = models.CharField(
        "Giới tính",
        max_length=20,
        choices=GENDER_CHOICES,
        default="Khác",
    )
    phone = models.CharField(
        "Số điện thoại",
        max_length=20,
        blank=True,
    )
    address = models.CharField(
        "Địa chỉ",
        max_length=255,
        blank=True,
    )
    email = models.EmailField("Email", blank=True)
    medical_history = models.TextField("Tiền sử bệnh", blank=True)
    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Bệnh nhân"
        verbose_name_plural = "Bệnh nhân"

    def __str__(self):
        return self.full_name


class Doctor(models.Model):
    full_name = models.CharField("Họ và tên", max_length=150)
    specialty = models.CharField("Chuyên khoa", max_length=100)
    phone = models.CharField(
        "Số điện thoại",
        max_length=20,
        blank=True,
    )
    email = models.EmailField("Email", blank=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Bác sĩ"
        verbose_name_plural = "Bác sĩ"

    def __str__(self):
        return f"{self.full_name} - {self.specialty}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Đã đặt lịch"),
        ("completed", "Đã khám"),
        ("cancelled", "Đã hủy"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Bệnh nhân",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Bác sĩ",
    )
    appointment_time = models.DateTimeField("Thời gian khám")
    reason = models.CharField("Lý do khám", max_length=255)
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled",
    )
    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["appointment_time"]
        verbose_name = "Lịch khám"
        verbose_name_plural = "Lịch khám"

    def __str__(self):
        return (
            f"{self.patient} - "
            f"{self.appointment_time:%d/%m/%Y %H:%M}"
        )


class MedicalRecord(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.PROTECT,
        related_name="medical_record",
        verbose_name="Lịch khám",
    )
    symptoms = models.TextField(
        "Triệu chứng",
        blank=True,
    )
    diagnosis = models.TextField("Chẩn đoán")
    treatment = models.TextField(
        "Phương pháp điều trị",
        blank=True,
    )
    notes = models.TextField(
        "Ghi chú",
        blank=True,
    )
    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "Ngày cập nhật",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Hồ sơ khám bệnh"
        verbose_name_plural = "Hồ sơ khám bệnh"

    def __str__(self):
        return (
            f"Hồ sơ #{self.pk} - "
            f"{self.appointment.patient.full_name}"
        )

class MedicalService(models.Model):
    code = models.CharField(
        "Mã dịch vụ",
        max_length=20,
        unique=True,
    )
    name = models.CharField(
        "Tên dịch vụ",
        max_length=150,
    )
    description = models.TextField(
        "Mô tả",
        blank=True,
    )
    price = models.DecimalField(
        "Đơn giá (VNĐ)",
        max_digits=12,
        decimal_places=0,
    )
    is_active = models.BooleanField(
        "Đang hoạt động",
        default=True,
    )
    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Dịch vụ y tế"
        verbose_name_plural = "Dịch vụ y tế"

    def __str__(self):
        return f"{self.code} - {self.name}"
# =========================================================
# HÓA ĐƠN VÀ THANH TOÁN
# =========================================================

import uuid
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Chưa thanh toán"),
        ("partial", "Thanh toán một phần"),
        ("paid", "Đã thanh toán"),
    ]

    code = models.CharField(
        "Mã hóa đơn",
        max_length=30,
        unique=True,
        editable=False,
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name="Lịch khám",
    )
    issued_at = models.DateTimeField(
        "Ngày lập hóa đơn",
        default=timezone.now,
    )
    notes = models.TextField("Ghi chú", blank=True)
    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "Hóa đơn"
        verbose_name_plural = "Hóa đơn"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"HD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(
            (item.line_total for item in self.items.all()),
            Decimal("0"),
        )

    @property
    def paid_amount(self):
        return sum(
            (
                payment.amount
                for payment in self.payments.filter(status="success")
            ),
            Decimal("0"),
        )

    @property
    def remaining_amount(self):
        return max(
            self.total_amount - self.paid_amount,
            Decimal("0"),
        )

    @property
    def payment_status(self):
        if self.total_amount <= 0 or self.paid_amount <= 0:
            return "unpaid"
        if self.paid_amount < self.total_amount:
            return "partial"
        return "paid"

    def __str__(self):
        return self.code


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Hóa đơn",
    )
    service = models.ForeignKey(
        MedicalService,
        on_delete=models.PROTECT,
        related_name="invoice_items",
        verbose_name="Dịch vụ",
    )
    service_name = models.CharField(
        "Tên dịch vụ tại thời điểm lập hóa đơn",
        max_length=150,
    )
    unit_price = models.DecimalField(
        "Đơn giá (VNĐ)",
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    quantity = models.PositiveIntegerField(
        "Số lượng",
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "Chi tiết hóa đơn"
        verbose_name_plural = "Chi tiết hóa đơn"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if self.service_id and not self.service_name:
            self.service_name = self.service.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_name} x {self.quantity}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Tiền mặt"),
        ("transfer", "Chuyển khoản"),
    ]
    STATUS_CHOICES = [
        ("success", "Thành công"),
        ("refunded", "Đã hoàn tiền"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Hóa đơn",
    )
    amount = models.DecimalField(
        "Số tiền (VNĐ)",
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1"))],
    )
    method = models.CharField(
        "Phương thức thanh toán",
        max_length=20,
        choices=METHOD_CHOICES,
        default="cash",
    )
    status = models.CharField(
        "Trạng thái giao dịch",
        max_length=20,
        choices=STATUS_CHOICES,
        default="success",
    )
    transaction_code = models.CharField(
        "Mã giao dịch",
        max_length=100,
        blank=True,
    )
    paid_at = models.DateTimeField(
        "Thời gian thanh toán",
        default=timezone.now,
    )
    notes = models.TextField("Ghi chú", blank=True)

    class Meta:
        ordering = ["-paid_at"]
        verbose_name = "Giao dịch thanh toán"
        verbose_name_plural = "Giao dịch thanh toán"

    def __str__(self):
        return f"{self.invoice.code} - {self.amount} VNĐ"

class Employee(models.Model):
    POSITION_CHOICES = [
        ("Admin", "Quản trị viên"),
        ("Doctor", "Bác sĩ"),
        ("Receptionist", "Nhân viên tiếp đón"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employee_profile",
        verbose_name="Tài khoản đăng nhập",
    )

    employee_code = models.CharField(
        "Mã nhân viên",
        max_length=20,
        unique=True,
    )

    full_name = models.CharField(
        "Họ và tên",
        max_length=150,
    )

    phone = models.CharField(
        "Số điện thoại",
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^0\d{9}$",
                message="Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.",
            )
        ],
    )

    email = models.EmailField(
        "Email",
        unique=True,
    )

    position = models.CharField(
        "Chức vụ",
        max_length=20,
        choices=POSITION_CHOICES,
    )

    start_date = models.DateField("Ngày vào làm")

    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["employee_code"]
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"

    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"
class Prescription(models.Model):
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.PROTECT,
        related_name="prescriptions",
        verbose_name="Hồ sơ khám bệnh",
    )
    prescribed_date = models.DateField(
        "Ngày kê đơn",
        auto_now_add=True,
    )
    instructions = models.TextField(
        "Lời dặn của bác sĩ",
        blank=True,
    )
    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-prescribed_date", "-id"]
        verbose_name = "Đơn thuốc"
        verbose_name_plural = "Đơn thuốc"

    def __str__(self):
        return (
            f"Đơn thuốc #{self.pk} - "
            f"{self.medical_record.appointment.patient.full_name}"
        )


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Đơn thuốc",
    )
    medicine_name = models.CharField(
        "Tên thuốc",
        max_length=200,
    )
    strength = models.CharField(
        "Hàm lượng",
        max_length=100,
        blank=True,
    )
    dosage = models.CharField(
        "Liều dùng mỗi lần",
        max_length=100,
    )
    frequency = models.CharField(
        "Số lần dùng",
        max_length=100,
    )
    duration_days = models.PositiveIntegerField(
        "Số ngày dùng",
    )
    quantity = models.PositiveIntegerField(
        "Số lượng",
    )
    usage_instructions = models.TextField(
        "Hướng dẫn sử dụng",
        blank=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Thuốc trong đơn"
        verbose_name_plural = "Thuốc trong đơn"

    def __str__(self):
        return self.medicine_name

