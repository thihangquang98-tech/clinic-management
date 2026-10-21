from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path("accounts/login/", views.login_view, name="login"),
    path("login/", views.login_view, name="login_page"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("", views.dashboard, name="dashboard"),

    path("patients/", views.patients, name="patients"),
    path("patients/add/", views.patient_create, name="patient_create"),
    path("patients/<int:pk>/edit/", views.patient_update, name="patient_update"),
    path("patients/<int:pk>/delete/", views.patient_delete, name="patient_delete"),

    path("doctors/", views.doctors, name="doctors"),
    path("doctors/add/", views.doctor_create, name="doctor_create"),
    path("doctors/<int:pk>/edit/", views.doctor_update, name="doctor_update"),
    path("doctors/<int:pk>/delete/", views.doctor_delete, name="doctor_delete"),

    path("appointments/", views.appointments, name="appointments"),
    path("appointments/add/", views.appointment_create, name="appointment_create"),
    path("appointments/<int:pk>/edit/", views.appointment_update, name="appointment_update"),
    path("appointments/<int:pk>/delete/", views.appointment_delete, name="appointment_delete"),
    path("medical-records/", views.medical_records, name="medical_records"),
    path("medical-records/add/", views.medical_record_create, name="medical_record_create"),
    path("medical-records/<int:pk>/edit/", views.medical_record_update, name="medical_record_update"),

    path("services/", views.medical_services, name="medical_services"),
    path("services/add/", views.medical_service_create, name="medical_service_create"),
    path("services/<int:pk>/edit/", views.medical_service_update, name="medical_service_update"),
    path("services/<int:pk>/delete/", views.medical_service_delete, name="medical_service_delete"),
    path( "data-overview/", views.data_overview, name="data_overview", ),
    path("reports/", views.reports, name="reports"),
    path("invoices/", views.invoices, name="invoices"),
    path("invoices/add/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/add-item/", views.invoice_add_item, name="invoice_add_item"),
    path("invoices/<int:pk>/add-payment/", views.invoice_add_payment, name="invoice_add_payment"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("prescriptions/", views.prescriptions, name="prescriptions"),
    path("prescriptions/add/", views.prescription_create, name="prescription_create"),
    path("prescriptions/<int:pk>/", views.prescription_detail, name="prescription_detail"),
    path("prescriptions/<int:pk>/add-item/", views.prescription_add_item, name="prescription_add_item"),
]
