
from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def role_required(*allowed_roles, allow_superuser=True):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if user.is_superuser and allow_superuser:
                return view_func(request, *args, **kwargs)

            if user.groups.filter(name__in=allowed_roles).exists():
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                "Bạn không có quyền truy cập chức năng này. "
                "Chỉ bác sĩ được phép tạo đơn thuốc."
            )
            return redirect("/")

        return wrapper
    return decorator

