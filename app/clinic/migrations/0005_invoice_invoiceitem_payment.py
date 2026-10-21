
import uuid
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0004_medicalservice"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        editable=False,
                        max_length=30,
                        unique=True,
                        verbose_name="Mã hóa đơn",
                    ),
                ),
                (
                    "issued_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Ngày lập hóa đơn",
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="Ghi chú"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Ngày tạo",
                    ),
                ),
                (
                    "appointment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="invoices",
                        to="clinic.appointment",
                        verbose_name="Lịch khám",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hóa đơn",
                "verbose_name_plural": "Hóa đơn",
                "ordering": ["-issued_at"],
            },
        ),
        migrations.CreateModel(
            name="InvoiceItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "service_name",
                    models.CharField(max_length=150),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        decimal_places=0,
                        max_digits=12,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0")
                            )
                        ],
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1)
                        ],
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="clinic.invoice",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="invoice_items",
                        to="clinic.medicalservice",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=0,
                        max_digits=12,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("1")
                            )
                        ],
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("cash", "Tiền mặt"),
                            ("transfer", "Chuyển khoản"),
                        ],
                        default="cash",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("success", "Thành công"),
                            ("refunded", "Đã hoàn tiền"),
                        ],
                        default="success",
                        max_length=20,
                    ),
                ),
                (
                    "transaction_code",
                    models.CharField(blank=True, max_length=100),
                ),
                (
                    "paid_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "notes",
                    models.TextField(blank=True),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payments",
                        to="clinic.invoice",
                    ),
                ),
            ],
            options={
                "ordering": ["-paid_at"],
            },
        ),
    ]
