
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Tạo các nhóm quyền của hệ thống ClinicCare"

    def handle(self, *args, **options):
        for name in ["Admin", "Doctor", "Receptionist"]:
            group, created = Group.objects.get_or_create(name=name)
            status = "đã tạo" if created else "đã tồn tại"
            self.stdout.write(f"Nhóm {name}: {status}")

        self.stdout.write(
            self.style.SUCCESS("Hoàn tất thiết lập nhóm quyền.")
        )
