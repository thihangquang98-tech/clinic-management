


from functools import wraps
from .models import Prescription, PrescriptionItem
from .forms import PrescriptionForm, PrescriptionItemForm
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login as auth_login
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from .models import Employee
from .forms import EmployeeForm

from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Invoice, InvoiceItem, Payment
from .forms import InvoiceForm, InvoiceItemForm, PaymentForm

from .decorators import role_required
from .models import (
    Appointment,
    Doctor,
    Patient,
    MedicalRecord,
    MedicalService,
)
from .forms import (
    PatientForm,
    DoctorForm,
    AppointmentForm,
    MedicalRecordForm,
    MedicalServiceForm,
)


# =========================================================
# TRANG TỔNG QUAN
# =========================================================

@role_required("Doctor", "Receptionist")
def dashboard(request):
    context = {

        "total_patients": Patient.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "total_appointments": Appointment.objects.count(),
        "patient_count": Patient.objects.count(),
        "doctor_count": Doctor.objects.count(),
        "appointment_count": Appointment.objects.count(),
        "total_services": MedicalService.objects.filter(
            is_active=True
        ).count(),
	
	"invoice_count": Invoice.objects.count(),

        "upcoming_appointments": Appointment.objects.filter(
            status="scheduled"
        ).order_by("appointment_time")[:10],
    }

    return render(request, "clinic/dashboard.html", context)


# =========================================================
# QUẢN LÝ BỆNH NHÂN
# Doctor: xem danh sách
# Receptionist: xem, thêm, sửa, xóa
# Admin: toàn quyền
# =========================================================

@role_required("Doctor", "Receptionist")
def patients(request):
    query = request.GET.get("q", "").strip()

    patient_list = Patient.objects.all()

    if query:
        patient_list = patient_list.filter(
            Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(address__icontains=query)
        )

    context = {
        "patients": patient_list,
        "query": query,
    }

    return render(request, "clinic/patients.html", context)
    



@role_required("Receptionist")
def patient_create(request):
    form = PatientForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thêm bệnh nhân thành công.")
        return redirect("patients")

    return render(
        request,
        "clinic/patient_form.html",
        {
            "form": form,
            "page_title": "Thêm bệnh nhân",
            "submit_label": "Lưu",
        },
    )



@role_required("Receptionist")
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật bệnh nhân thành công.")
        return redirect("patients")

    return render(request, "clinic/patient_form.html", {
        "form": form,
        "page_title": "Sửa thông tin bệnh nhân",
        "submit_label": "Lưu thay đổi",
        "patient": patient,
    })

@require_POST
@role_required("Receptionist")
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    try:
        patient.delete()
        messages.success(request, "Đã xóa bệnh nhân.")
    except Exception:
        messages.error(
            request,
            "Không thể xóa bệnh nhân vì đang có dữ liệu liên quan.",
        )

    return redirect("patients")


# =========================================================
# QUẢN LÝ BÁC SĨ
# Doctor và Receptionist: xem danh sách
# Admin: toàn quyền quản lý
# =========================================================

@role_required("Doctor", "Receptionist")
def doctors(request):
    query = request.GET.get("q", "").strip()

    doctor_list = Doctor.objects.all()

    if query:
        doctor_list = doctor_list.filter(
            Q(full_name__icontains=query)
            | Q(specialty__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )

    return render(
        request,
        "clinic/doctors.html",
        {"doctors": doctor_list, "query": query},
    )


@role_required("Admin")
def doctor_create(request):
    form = DoctorForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thêm bác sĩ thành công.")
        return redirect("doctors")

    return render(request, "clinic/doctor_form.html", {
        "form": form,
        "page_title": "Thêm bác sĩ",
        "submit_label": "Lưu",
    })

@role_required("Admin")
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doctor)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật bác sĩ thành công.")
        return redirect("doctors")

    return render(request, "clinic/doctor_form.html", {
        "form": form,
        "page_title": "Sửa thông tin bác sĩ",
        "submit_label": "Lưu thay đổi",
        "doctor": doctor,
    })

@require_POST
@role_required("Admin")
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)

    try:
        doctor.delete()
        messages.success(request, "Đã xóa bác sĩ.")
    except Exception:
        messages.error(
            request,
            "Không thể xóa bác sĩ vì đang có lịch khám liên quan.",
        )

    return redirect("doctors")


# =========================================================
# QUẢN LÝ LỊCH KHÁM
# Receptionist: thêm, sửa, xóa
# Doctor: xem danh sách
# Admin: toàn quyền
# =========================================================

@role_required("Doctor", "Receptionist")
def appointments(request):
    query = request.GET.get("q", "").strip()

    appointment_list = Appointment.objects.select_related(
        "patient", "doctor"
    ).all()

    if query:
        appointment_list = appointment_list.filter(
            Q(patient__full_name__icontains=query)
            | Q(doctor__full_name__icontains=query)
            | Q(reason__icontains=query)
            | Q(status__icontains=query)
        )

    return render(
        request,
        "clinic/appointments.html",
        {
            "appointments": appointment_list,
            "query": query,
        },
    )


@role_required("Receptionist")
def appointment_create(request):
    form = AppointmentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tạo lịch khám thành công.")
        return redirect("appointments")

    return render(request, "clinic/appointment_form.html", {
        "form": form,
        "page_title": "Thêm lịch khám",
        "submit_label": "Lưu",
    })

@role_required("Receptionist")
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật lịch khám thành công.")
        return redirect("appointments")

    return render(request, "clinic/appointment_form.html", {
        "form": form,
        "page_title": "Sửa lịch khám",
        "submit_label": "Lưu thay đổi",
        "appointment": appointment,
    })

@require_POST
@role_required("Receptionist")
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    try:
        appointment.delete()
        messages.success(request, "Đã xóa lịch khám.")
    except Exception:
        messages.error(
            request,
            "Không thể xóa lịch khám vì có hồ sơ bệnh án liên quan.",
        )

    return redirect("appointments")


# =========================================================
# HỒ SƠ BỆNH ÁN
# Doctor: xem, tạo và cập nhật
# Admin: toàn quyền
# ================
@role_required("Doctor", "Receptionist")
def medical_records(request):
    query = request.GET.get("q", "").strip()

    record_list = MedicalRecord.objects.select_related(
        "appointment",
        "appointment__patient",
        "appointment__doctor",
    ).all()

    if query:
        record_list = record_list.filter(
            Q(appointment__patient__full_name__icontains=query)
            | Q(appointment__doctor__full_name__icontains=query)
            | Q(diagnosis__icontains=query)
        )

    return render(
        request,
        "clinic/medical_records.html",
        {
            "medical_records": record_list,
            "records": record_list,
            "query": query,
        },
    )


@role_required("Doctor")
def medical_record_create(request):
    form = MedicalRecordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tạo hồ sơ bệnh án thành công.")
        return redirect("medical_records")

    return render(request, "clinic/medical_record_form.html", {
        "form": form,
        "page_title": "Thêm hồ sơ khám bệnh",
        "submit_label": "Lưu",
    })

@role_required("Doctor")
def medical_record_update(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    form = MedicalRecordForm(request.POST or None, instance=record)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật hồ sơ bệnh án thành công.")
        return redirect("medical_records")

    return render(request, "clinic/medical_record_form.html", {
        "form": form,
        "page_title": "Sửa hồ sơ khám bệnh",
        "submit_label": "Lưu thay đổi",
        "record": record,
    })

# =========================================================
# QUẢN LÝ ĐƠN THUỐC
# =========================================================
@role_required("Doctor", allow_superuser=False)
def prescriptions(request):
    prescription_list = Prescription.objects.select_related(
        "medical_record",
        "medical_record__appointment",
        "medical_record__appointment__patient",
        "medical_record__appointment__doctor",
    ).prefetch_related("items")

    query = request.GET.get("q", "").strip()

    if query:
        prescription_list = prescription_list.filter(
            Q(
                medical_record__appointment__patient__full_name__icontains=query
            )
            | Q(
                medical_record__appointment__doctor__full_name__icontains=query
            )
        )

    return render(
        request,
        "clinic/prescriptions.html",
        {
            "prescriptions": prescription_list,
            "query": query,
        },
    )


@role_required("Doctor", allow_superuser=False)
def prescription_create(request):
    form = PrescriptionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        prescription = form.save()
        messages.success(request, "Tạo đơn thuốc thành công.")
        return redirect("prescription_detail", pk=prescription.pk)

    return render(
        request,
        "clinic/prescription_form.html",
        {
            "form": form,
            "title": "Tạo đơn thuốc",
        },
    )

# =========================================================
# QUẢN LÝ DỊCH VỤ Y TẾ
# Doctor và Receptionist: xem danh sách
# Admin: thêm, sửa, xóa
# =========================================================

@role_required("Doctor", "Receptionist")
def medical_services(request):
    query = request.GET.get("q", "").strip()

    service_list = MedicalService.objects.all()

    if query:
        service_list = service_list.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(description__icontains=query)
        )

    return render(
        request,
        "clinic/medical_services.html",
        {
            "medical_services": service_list,
            "services": service_list,
            "query": query,
        },
    )


@role_required("Admin")
def medical_service_create(request):
    form = MedicalServiceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thêm dịch vụ y tế thành công.")
        return redirect("medical_services")

    return render(request, "clinic/medical_service_form.html", {
        "form": form,
        "page_title": "Thêm dịch vụ y tế",
        "submit_label": "Lưu",
    })

@role_required("Admin")
def medical_service_update(request, pk):
    service = get_object_or_404(MedicalService, pk=pk)
    form = MedicalServiceForm(request.POST or None, instance=service)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật dịch vụ y tế thành công.")
        return redirect("medical_services")

    return render(request, "clinic/medical_service_form.html", {
        "form": form,
        "page_title": "Sửa dịch vụ y tế",
        "submit_label": "Lưu thay đổi",
        "service": service,
    })

@require_POST
@role_required("Admin")
def medical_service_delete(request, pk):
    service = get_object_or_404(MedicalService, pk=pk)
    service.delete()
    messages.success(request, "Đã xóa dịch vụ y tế.")
    return redirect("medical_services")


# =========================================================
# TRANG TỪ CHỐI TRUY CẬP
# =========================================================



# =========================================================
# ĐĂNG NHẬP
# =========================================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        # Hỗ trợ đăng nhập bằng email nếu email khớp một tài khoản.
        if user is None and "@" in username:
            User = get_user_model()
            matching_users = User.objects.filter(email__iexact=username)
            if matching_users.count() == 1:
                account = matching_users.first()
                user = authenticate(
                    request,
                    username=account.get_username(),
                    password=password,
                )

        if user is not None and user.is_active:
            auth_login(request, user)

            if request.POST.get("remember_me"):
                request.session.set_expiry(60 * 60 * 24 * 14)
            else:
                request.session.set_expiry(0)

            if (
                next_url
                and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                )
            ):
                return redirect(next_url)

            return redirect("dashboard")

        messages.error(
            request,
            "Tên đăng nhập/email hoặc mật khẩu không chính xác.",
        )

    return render(
        request,
        "clinic/login.html",
        {"next": next_url},
    )


def access_denied(request):
    return render(
        request,
        "clinic/access_denied.html",
        status=403,
    )


# =========================================================
# ĐĂNG XUẤT
# Chỉ chấp nhận POST để tránh đăng xuất qua liên kết GET.
# =========================================================

@require_POST
@login_required(login_url="login")
def clinic_logout(request):
    logout(request)
    messages.success(request, "Bạn đã đăng xuất thành công.")
    return redirect("login")

# ============================
# TỔNG QUAN QUẢN TRỊ DỮ LIỆU
# ============================


@login_required
@role_required("Doctor", "Receptionist")
def data_overview(request):
    """Báo cáo thống kê phòng khám theo khoảng thời gian."""
    from datetime import datetime, time, timedelta
    from django.utils import timezone
    from django.db.models import Sum
    from .models import Invoice, Payment

    today = timezone.localdate()
    default_start = today.replace(day=1)

    start_raw = request.GET.get("start_date", default_start.isoformat())
    end_raw = request.GET.get("end_date", today.isoformat())

    try:
        start_date = datetime.strptime(start_raw, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_raw, "%Y-%m-%d").date()
        if start_date > end_date:
            raise ValueError("Ngày bắt đầu phải trước ngày kết thúc.")
    except ValueError:
        start_date = default_start
        end_date = today

    start_dt = timezone.make_aware(
        datetime.combine(start_date, time.min)
    )
    end_dt = timezone.make_aware(
        datetime.combine(end_date + timedelta(days=1), time.min)
    )

    appointments = Appointment.objects.all()
    period_appointments = appointments.filter(
        appointment_time__gte=start_dt,
        appointment_time__lt=end_dt,
    )

    payments = Payment.objects.filter(
        status="success",
        paid_at__gte=start_dt,
        paid_at__lt=end_dt,
    )
    revenue = payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    # Tổng giá trị hóa đơn được lập trong khoảng thời gian.
    invoices = Invoice.objects.filter(
        issued_at__gte=start_dt,
        issued_at__lt=end_dt,
    )
    invoice_total = Decimal("0")
    for invoice in invoices.prefetch_related("items"):
        invoice_total += invoice.total_amount

    daily_stats = []
    current_day = start_date
    while current_day <= end_date:
        day_start = timezone.make_aware(
            datetime.combine(current_day, time.min)
        )
        day_end = day_start + timedelta(days=1)

        daily_stats.append({
            "label": current_day.strftime("%d/%m"),
            "appointments": period_appointments.filter(
                appointment_time__gte=day_start,
                appointment_time__lt=day_end,
            ).count(),
            "revenue": payments.filter(
                paid_at__gte=day_start,
                paid_at__lt=day_end,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0"),
        })
        current_day += timedelta(days=1)

    context = {
        "total_patients": Patient.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "total_appointments": appointments.count(),
        "total_records": MedicalRecord.objects.count(),
        "total_services": MedicalService.objects.count(),

        "scheduled_count": period_appointments.filter(
            status="scheduled"
        ).count(),
        "completed_count": period_appointments.filter(
            status="completed"
        ).count(),
        "cancelled_count": period_appointments.filter(
            status="cancelled"
        ).count(),
        "period_appointments_count": period_appointments.count(),

        "revenue": revenue,
        "invoice_total": invoice_total,
        "remaining_amount": max(invoice_total - revenue, Decimal("0")),
        "daily_stats": daily_stats,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),

        "recent_appointments": appointments.select_related(
            "patient", "doctor"
        ).order_by("-created_at")[:8],
        "updated_at": timezone.localtime(),
    }

    return render(request, "clinic/data_overview.html", context)

# =========================================================
# QUẢN LÝ HÓA ĐƠN VÀ THANH TOÁN
# Admin và Receptionist
# ================================================

@role_required("Admin", "Receptionist")
def invoices(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    invoice_list = Invoice.objects.select_related(
        "appointment",
        "appointment__patient",
        "appointment__doctor",
    ).prefetch_related("items", "payments")

    if query:
        invoice_list = invoice_list.filter(
            Q(code__icontains=query)
            | Q(appointment__patient__full_name__icontains=query)
            | Q(appointment__doctor__full_name__icontains=query)
        )

    if status_filter in ("unpaid", "partial", "paid"):
        filtered_ids = [
            invoice.pk
            for invoice in invoice_list
            if invoice.payment_status == status_filter
        ]
        invoice_list = invoice_list.filter(pk__in=filtered_ids)

    return render(
        request,
        "clinic/invoices.html",
        {
            "invoices": invoice_list,
            "query": query,
            "status_filter": status_filter,
        },
    )


@role_required("Admin", "Receptionist")
def invoice_create(request):
    form = InvoiceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        appointment = form.cleaned_data["appointment"]

        # Tránh tạo hóa đơn trùng cho cùng lịch khám.
        if Invoice.objects.filter(appointment=appointment).exists():
            form.add_error(
                "appointment",
                "Lịch khám này đã có hóa đơn.",
            )
        else:
            invoice = form.save()
            messages.success(
                request,
                "Tạo hóa đơn thành công. Hãy thêm dịch vụ y tế.",
            )
            return redirect("invoice_detail", pk=invoice.pk)

    return render(
        request,
        "clinic/invoice_form.html",
        {
            "form": form,
            "title": "Tạo hóa đơn",
        },
    )


@role_required("Admin", "Receptionist")
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related(
            "appointment",
            "appointment__patient",
            "appointment__doctor",
        ).prefetch_related("items__service", "payments"),
        pk=pk,
    )

    item_form = InvoiceItemForm()
    payment_form = PaymentForm(invoice=invoice)

    return render(
        request,
        "clinic/invoice_detail.html",
        {
            "invoice": invoice,
            "item_form": item_form,
            "payment_form": payment_form,
        },
    )


@require_POST
@role_required("Admin", "Receptionist")
def invoice_add_item(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceItemForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Vui lòng kiểm tra dịch vụ và số lượng.")
        return redirect("invoice_detail", pk=pk)

    service = form.cleaned_data["service"]
    quantity = form.cleaned_data["quantity"]

    if quantity < 1:
        messages.error(request, "Số lượng phải ít nhất là 1.")
        return redirect("invoice_detail", pk=pk)

    try:
        with transaction.atomic():
            locked_invoice = Invoice.objects.select_for_update().get(pk=pk)

            if locked_invoice.payments.filter(status="success").exists():
                messages.error(
                    request,
                    "Không thể thay đổi dịch vụ sau khi đã thanh toán. "
                    "Hãy xử lý điều chỉnh theo quy trình của phòng khám.",
                )
                return redirect("invoice_detail", pk=pk)

            InvoiceItem.objects.create(
                invoice=locked_invoice,
                service=service,
                service_name=service.name,
                unit_price=service.price,
                quantity=quantity,
            )

        messages.success(request, "Đã thêm dịch vụ vào hóa đơn.")

    except Exception:
        messages.error(request, "Không thể thêm dịch vụ. Vui lòng thử lại.")

    return redirect("invoice_detail", pk=pk)


@require_POST
@role_required("Admin", "Receptionist")
def invoice_add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = PaymentForm(request.POST, invoice=invoice)

    if not form.is_valid():
        messages.error(
            request,
            "Thông tin thanh toán không hợp lệ. "
            + "; ".join(
                f"{field}: {', '.join(errors)}"
                for field, errors in form.errors.items()
            ),
        )
        return redirect("invoice_detail", pk=pk)

    try:
        with transaction.atomic():
            locked_invoice = Invoice.objects.select_for_update().get(pk=pk)
            amount = form.cleaned_data["amount"]

            if amount > locked_invoice.remaining_amount:
                messages.error(
                    request,
                    "Số tiền vượt quá số dư còn phải trả. Vui lòng kiểm tra lại.",
                )
                return redirect("invoice_detail", pk=pk)

            if locked_invoice.total_amount <= 0:
                messages.error(
                    request,
                    "Hãy thêm dịch vụ vào hóa đơn trước khi thanh toán.",
                )
                return redirect("invoice_detail", pk=pk)

            payment = form.save(commit=False)
            payment.invoice = locked_invoice
            payment.status = "success"
            payment.save()

        messages.success(request, "Ghi nhận thanh toán thành công.")

    except Exception:
        messages.error(
            request,
            "Không thể ghi nhận thanh toán. Vui lòng kiểm tra lại.",
        )

    return redirect("invoice_detail", pk=pk)
# =========================================================
# QUẢN LÝ NHÂN VIÊN - CHỈ ADMIN
# =========================================================

User = get_user_model()


@role_required("Admin")
def employee_list(request):
    query = request.GET.get("q", "").strip()

    employee_list = Employee.objects.select_related("user").all()

    if query:
        employee_list = employee_list.filter(
            Q(employee_code__icontains=query)
            | Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(user__username__icontains=query)
        )

    employees = list(employee_list)

    doctor_count = sum(
        1 for employee in employees
        if employee.position == "Doctor"
    )
    receptionist_count = sum(
        1 for employee in employees
        if employee.position == "Receptionist"
    )

    return render(
        request,
        "clinic/employees.html",
        {
            "employees": employees,
            "query": query,
            "doctor_count": doctor_count,
            "receptionist_count": receptionist_count,
        },
    )



@role_required("Admin")
def employee_create(request):
    form = EmployeeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                employee = form.save(commit=False)

                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]

                user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data["email"],
                    password=password,
                    first_name=form.cleaned_data["full_name"],
                )

                group = Group.objects.get(
                    name=form.cleaned_data["position"]
                )
                user.groups.add(group)

                employee.user = user
                employee.save()

            messages.success(
                request,
                "Đã tạo hồ sơ và tài khoản nhân viên thành công.",
            )
            return redirect("employee_list")

        except Exception:
            messages.error(
                request,
                "Không thể tạo nhân viên. "
                "Vui lòng kiểm tra dữ liệu và thử lại.",
            )

    return render(
        request,
        "clinic/employee_form.html",
        {
            "form": form,
            "page_title": "Thêm nhân viên",
            "is_edit": False,
        },
    )


@role_required("Admin")
def employee_update(request, pk):
    employee = get_object_or_404(
        Employee.objects.select_related("user"),
        pk=pk,
    )

    form = EmployeeForm(
        request.POST or None,
        instance=employee,
    )

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                employee = form.save(commit=False)
                user = employee.user

                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]

                user.username = username
                user.email = form.cleaned_data["email"]
                user.first_name = form.cleaned_data["full_name"]

                if password:
                    user.set_password(password)

                user.save()

                group = Group.objects.get(
                    name=form.cleaned_data["position"]
                )
                user.groups.set([group])

                employee.save()

            messages.success(
                request,
                "Đã cập nhật thông tin nhân viên thành công.",
            )
            return redirect("employee_list")

        except Exception:
            messages.error(
                request,
                "Không thể cập nhật nhân viên. "
                "Vui lòng kiểm tra dữ liệu và thử lại.",
            )

    return render(
        request,
        "clinic/employee_form.html",
        {
            "form": form,
            "page_title": "Sửa thông tin nhân viên",
            "is_edit": True,
        },
    )


@login_required
@role_required("Doctor", "Receptionist")
def reports(request):
    import calendar
    from datetime import date, timedelta
    from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
    from django.db.models.functions import TruncDate
    from django.utils import timezone
    from .models import Invoice, InvoiceItem, Payment, MedicalRecord

    today = timezone.localdate()

    try:
        month = int(request.GET.get("month", today.month))
        year = int(request.GET.get("year", today.year))
        if not 1 <= month <= 12 or not 2000 <= year <= 2100:
            raise ValueError
    except (TypeError, ValueError):
        month, year = today.month, today.year

    last_day = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = min(date(year, month, last_day), today) if (
        year, month
    ) == (today.year, today.month) else date(year, month, last_day)

    appointments = Appointment.objects.filter(
        appointment_time__date__gte=start_date,
        appointment_time__date__lte=end_date,
    )
    patients = Patient.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )
    records = MedicalRecord.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )
    invoices = Invoice.objects.filter(
        issued_at__date__gte=start_date,
        issued_at__date__lte=end_date,
    )

    successful_payments = Payment.objects.filter(
        status="success",
        paid_at__date__gte=start_date,
        paid_at__date__lte=end_date,
    )
    paid_revenue = successful_payments.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    invoice_totals = invoices.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("items__unit_price") * F("items__quantity"),
                output_field=DecimalField(max_digits=14, decimal_places=0),
            )
        )
    )["total"] or Decimal("0")

    daily_patients = {
        row["day"]: row["count"]
        for row in patients.annotate(day=TruncDate("created_at"))
        .values("day").annotate(count=Count("id"))
    }
    daily_appointments = {
        row["day"]: row["count"]
        for row in appointments.annotate(
            day=TruncDate("appointment_time")
        ).values("day").annotate(count=Count("id"))
    }

    chart_labels = []
    patient_counts = []
    appointment_counts = []
    current_day = start_date
    while current_day <= end_date:
        chart_labels.append(current_day.day)
        patient_counts.append(daily_patients.get(current_day, 0))
        appointment_counts.append(daily_appointments.get(current_day, 0))
        current_day += timedelta(days=1)

    service_stats = (
        InvoiceItem.objects.filter(
            invoice__issued_at__date__gte=start_date,
            invoice__issued_at__date__lte=end_date,
        )
        .values("service_name")
        .annotate(
            invoice_count=Count("invoice", distinct=True),
            total_value=Sum(
                ExpressionWrapper(
                    F("unit_price") * F("quantity"),
                    output_field=DecimalField(max_digits=14, decimal_places=0),
                )
            ),
        )
        .order_by("-total_value")
    )

    invoice_status = {
        "paid": 0,
        "partial": 0,
        "unpaid": 0,
    }
    for invoice in invoices.prefetch_related("items", "payments"):
        invoice_status[invoice.payment_status] += 1

    context = {
        "month": month,
        "year": year,
        "month_choices": [(i, calendar.month_name[i]) for i in range(1, 13)],
        "year_choices": range(max(2020, today.year - 5), today.year + 2),
        "total_patients": patients.count(),
        "total_appointments": appointments.count(),
        "total_records": records.count(),
        "total_invoices": invoices.count(),
        "paid_revenue": paid_revenue,
        "invoice_totals": invoice_totals,
        "paid_count": invoice_status["paid"],
        "partial_count": invoice_status["partial"],
        "unpaid_count": invoice_status["unpaid"],
        "chart_labels": chart_labels,
        "patient_counts": patient_counts,
        "appointment_counts": appointment_counts,
        "service_stats": service_stats,
        "updated_at": timezone.localtime(),
    }
    return render(request, "clinic/reports.html", context)




# Khôi phục chức năng xem chi tiết đơn thuốc
@role_required("Doctor")
def prescription_detail(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related(
            "medical_record",
            "medical_record__appointment",
            "medical_record__appointment__patient",
            "medical_record__appointment__doctor",
        ).prefetch_related("items"),
        pk=pk,
    )

    item_form = PrescriptionItemForm()

    return render(
        request,
        "clinic/prescription_detail.html",
        {
            "prescription": prescription,
            "item_form": item_form,
        },
    )


# Khôi phục chức năng thêm thuốc vào đơn
@role_required("Doctor")
def prescription_add_item(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    if request.method != "POST":
        return redirect("prescription_detail", pk=pk)

    form = PrescriptionItemForm(request.POST)

    if form.is_valid():
        item = form.save(commit=False)
        item.prescription = prescription
        item.save()
        messages.success(request, "Đã thêm thuốc vào đơn thành công.")
    else:
        messages.error(request, "Thông tin thuốc chưa hợp lệ.")

    return redirect("prescription_detail", pk=pk)
