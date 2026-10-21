# Generated for the clinic management application.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Doctor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=150)),
                ("specialty", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=20, blank=True)),
                ("email", models.EmailField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=150)),
                ("date_of_birth", models.DateField(null=True, blank=True)),
                ("gender", models.CharField(max_length=10, default="Khác")),
                ("phone", models.CharField(max_length=20, blank=True)),
                ("address", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("appointment_time", models.DateTimeField()),
                ("reason", models.CharField(max_length=255, blank=True)),
                ("status", models.CharField(max_length=20, default="scheduled")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="clinic.doctor")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="clinic.patient")),
            ],
        ),
    ]
