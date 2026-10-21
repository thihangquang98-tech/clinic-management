
from django.contrib import admin
from .models import (
    Patient,
    Doctor,
    Appointment,
    MedicalRecord,
    MedicalService,
    Invoice,
    InvoiceItem,
    Payment,
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "date_of_birth", "gender", "phone")
    search_fields = ("full_name", "phone")
    list_per_page = 20


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "specialty", "phone", "email")
    search_fields = ("full_name", "specialty", "phone")
    list_per_page = 20


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "appointment_time",
        "status",
    )
    search_fields = ("patient__full_name", "doctor__full_name")
    list_filter = ("status",)
    list_per_page = 20


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "appointment",
        "diagnosis",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "appointment__patient__full_name",
        "diagnosis",
        "symptoms",
    )
    list_per_page = 20


@admin.register(MedicalService)
class MedicalServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "price", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active",)
    list_per_page = 20


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ("service_name", "unit_price")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("code", "appointment", "issued_at", "display_total")
    search_fields = (
        "code",
        "appointment__patient__full_name",
    )
    list_filter = ("issued_at",)
    readonly_fields = ("code",)
    inlines = (InvoiceItemInline,)
    list_per_page = 20

    @admin.display(description="Tổng tiền (VNĐ)")
    def display_total(self, obj):
        return obj.total_amount


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "service_name", "quantity", "unit_price")
    search_fields = ("invoice__code", "service_name")
    list_per_page = 20


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "amount",
        "method",
        "status",
        "paid_at",
    )
    search_fields = ("invoice__code", "transaction_code")
    list_filter = ("method", "status", "paid_at")
    list_per_page = 20

