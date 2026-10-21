from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0003_medicalrecord"),
    ]

    operations = [
        migrations.CreateModel(
            name="MedicalService",
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
                        max_length=20,
                        unique=True,
                        verbose_name="Mã dịch vụ",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150,
                        verbose_name="Tên dịch vụ",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Mô tả"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=0,
                        max_digits=12,
                        verbose_name="Đơn giá (VNĐ)",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        verbose_name="Đang hoạt động",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Ngày tạo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dịch vụ y tế",
                "verbose_name_plural": "Dịch vụ y tế",
                "ordering": ["name"],
            },
        ),
    ]
