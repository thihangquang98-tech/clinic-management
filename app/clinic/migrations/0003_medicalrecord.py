from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0002_alter_appointment_options_alter_doctor_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MedicalRecord",
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
                    "symptoms",
                    models.TextField(blank=True, verbose_name="Triệu chứng"),
                ),
                (
                    "diagnosis",
                    models.TextField(verbose_name="Chẩn đoán"),
                ),
                (
                    "treatment",
                    models.TextField(
                        blank=True,
                        verbose_name="Phương pháp điều trị",
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
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="Ngày cập nhật",
                    ),
                ),
                (
                    "appointment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="medical_record",
                        to="clinic.appointment",
                        verbose_name="Lịch khám",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hồ sơ khám bệnh",
                "verbose_name_plural": "Hồ sơ khám bệnh",
                "ordering": ["-created_at"],
            },
        ),
    ]
