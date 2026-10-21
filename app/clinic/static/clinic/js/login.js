(() => {
    "use strict";

    const form = document.getElementById("login-form");
    if (!form) return;

    const username = document.getElementById("id_username");
    const password = document.getElementById("id_password");
    const toggle = document.getElementById("password-toggle");
    const submitButton = document.getElementById("submit-button");
    const submitLabel = submitButton.querySelector(".submit-label");
    const usernameError = document.getElementById("username-error");
    const passwordError = document.getElementById("password-error");
    const formError = document.getElementById("form-error");
    const rememberMe = document.getElementById("remember-me");
    const roleInput = document.getElementById("selected-role");
    const roleButtons = document.querySelectorAll(".role-option");
    const forgotLink = document.getElementById("forgot-link");

    // Hiện/ẩn mật khẩu, không gửi mật khẩu tới bất kỳ dịch vụ bên ngoài nào.
    toggle.addEventListener("click", () => {
        const showing = password.type === "password";
        password.type = showing ? "text" : "password";
        toggle.classList.toggle("is-visible", showing);
        toggle.setAttribute("aria-pressed", String(showing));
        toggle.setAttribute("aria-label", showing ? "Ẩn mật khẩu" : "Hiện mật khẩu");
        password.focus();
    });

    // Vai trò chỉ là lựa chọn giao diện; không có quyền cấp vai trò ở frontend.
    roleButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const alreadySelected = button.classList.contains("is-selected");

            roleButtons.forEach((item) => {
                item.classList.remove("is-selected");
                item.setAttribute("aria-pressed", "false");
            });

            if (alreadySelected) {
                roleInput.value = "";
                return;
            }

            button.classList.add("is-selected");
            button.setAttribute("aria-pressed", "true");
            roleInput.value = button.dataset.role;
        });
    });

    function clearFieldError(input, errorElement) {
        errorElement.textContent = "";
        input.closest(".input-wrap").classList.remove("has-error");
        input.removeAttribute("aria-invalid");
    }

    username.addEventListener("input", () => clearFieldError(username, usernameError));
    password.addEventListener("input", () => clearFieldError(password, passwordError));

    // Django LoginView hiện xác thực tên đăng nhập. Không giả lập email login
    // khi backend chưa có cơ chế tra cứu email.
    form.addEventListener("submit", (event) => {
        clearFieldError(username, usernameError);
        clearFieldError(password, passwordError);
        formError.textContent = "";

        let firstInvalid = null;

        if (!username.value.trim()) {
            usernameError.textContent = "Vui lòng nhập tên đăng nhập.";
            username.closest(".input-wrap").classList.add("has-error");
            username.setAttribute("aria-invalid", "true");
            firstInvalid = username;
        }

        if (!password.value) {
            passwordError.textContent = "Vui lòng nhập mật khẩu.";
            password.closest(".input-wrap").classList.add("has-error");
            password.setAttribute("aria-invalid", "true");
            firstInvalid = firstInvalid || password;
        }

        if (firstInvalid) {
            event.preventDefault();
            firstInvalid.focus();
            return;
        }

        // Ghi nhớ lựa chọn trên thiết bị bằng checkbox native của trình duyệt.
        // Không lưu mật khẩu hoặc thông tin bí mật vào localStorage/cookie tự tạo.
        // Session và thời hạn đăng nhập vẫn do Django quản lý.
        try {
            if (rememberMe.checked) {
                username.setAttribute("autocomplete", "username");
            }
        } catch (_) {
            // Không cản trở việc đăng nhập nếu trình duyệt hạn chế API.
        }

        submitButton.disabled = true;
        submitButton.classList.add("is-loading");
        submitLabel.textContent = "Đang đăng nhập...";
    });

    forgotLink.addEventListener("click", (event) => {
        event.preventDefault();
        formError.textContent =
            "Vui lòng liên hệ quản trị viên để được hỗ trợ đặt lại mật khẩu.";
    });
})();
