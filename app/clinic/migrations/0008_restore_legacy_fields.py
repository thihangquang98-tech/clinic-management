from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clinic", "0007_alter_invoiceitem_options_alter_payment_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="Email"),
        ),
        migrations.AddField(
            model_name="patient",
            name="medical_history",
            field=models.TextField(blank=True, verbose_name="Tiền sử bệnh"),
        ),
    ]
