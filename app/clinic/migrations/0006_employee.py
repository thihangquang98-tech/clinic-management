from django.conf import settings
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0005_invoice_invoiceitem_payment"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Employee",
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
                    "employee_code",
                    models.CharField(
                        max_length=20,
                        unique=True,
                        verbose_name="Mã nhân viên",
                    ),
                ),
                (
                    "full_name",
                    models.CharField(
                        max_length=150,
                        verbose_name="Họ và tên",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        max_length=10,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                regex=r"^0\d{9}$",
                                message=(
                                    "Số điện thoại phải gồm 10 chữ số "
                                    "và bắt đầu bằng 0."
                                ),
                            )
                        ],
                        verbose_name="Số điện thoại",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254,
                        unique=True,
                        verbose_name="Email",
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        choices=[
                            ("Admin", "Quản trị viên"),
                            ("Doctor", "Bác sĩ"),
                            ("Receptionist", "Nhân viên tiếp đón"),
                        ],
                        max_length=20,
                        verbose_name="Chức vụ",
                    ),
                ),
                (
                    "start_date",
                    models.DateField(verbose_name="Ngày vào làm"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Ngày tạo",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=models.PROTECT,
                        related_name="employee_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Tài khoản đăng nhập",
                    ),
                ),
            ],
            options={
                "verbose_name": "Nhân viên",
                "verbose_name_plural": "Nhân viên",
                "ordering": ["employee_code"],
            },
        ),
    ]
