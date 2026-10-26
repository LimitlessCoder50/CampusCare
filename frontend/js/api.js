/**
 * CampusCare API & Authentication Client
 */

const API_BASE = "http://127.0.0.1:8000/api/v1";

/**
 * Toggle password visibility between text and password
 */
function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
    }
}

/**
 * Display a user feedback message
 */
function showFeedback(boxId, message, type = "error") {
    const box = document.getElementById(boxId);
    if (!box) return;

    box.className = `feedback-box ${type}`;
    let iconClass = "bi-exclamation-triangle-fill";
    if (type === "success") iconClass = "bi-check-circle-fill";
    if (type === "info") iconClass = "bi-info-circle-fill";

    box.innerHTML = `<i class="bi ${iconClass} flex-shrink-0"></i><div>${message}</div>`;
    box.style.display = "flex";
}

function hideFeedback(boxId) {
    const box = document.getElementById(boxId);
    if (box) box.style.display = "none";
}

/**
 * Set button into loading spinner state
 */
function setButtonLoading(btn, isLoading, defaultText = "Submit") {
    if (!btn) return;
    if (isLoading) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...`;
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalText || defaultText;
    }
}

/**
 * Authenticate user against FastAPI backend & verify role compatibility
 */
async function handleLogin({ email, password, portalRole, feedbackId, submitBtn }) {
    hideFeedback(feedbackId);
    setButtonLoading(submitBtn, true);

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed. Please verify your credentials.");
        }

        // Verify that the logged-in role is authorized for this portal
        const role = data.role;
        let isAuthorized = false;

        if (portalRole === "user") {
            isAuthorized = (role === "student" || role === "faculty");
        } else if (portalRole === "maintenance") {
            isAuthorized = (role === "maintenance" || role === "admin");
        } else if (portalRole === "admin") {
            isAuthorized = (role === "admin");
        }

        if (!isAuthorized) {
            let roleTitle = role.toUpperCase();
            if (role === "student") roleTitle = "Student";
            if (role === "faculty") roleTitle = "Faculty";
            if (role === "maintenance") roleTitle = "Maintenance Personnel";

            throw new Error(
                `Access Restricted: Your account is registered as <strong>${roleTitle}</strong>. ` +
                `Please sign in via the designated portal.`
            );
        }

        // Store session tokens & user info
        localStorage.setItem("campuscare_token", data.access_token);
        localStorage.setItem("campuscare_role", data.role);
        localStorage.setItem("campuscare_user", JSON.stringify(data.profile));

        showFeedback(feedbackId, `Welcome back! Authentication successful. Redirecting...`, "success");

        // Redirect or trigger portal dashboard
        setTimeout(() => {
            alert(`Login successful as ${data.role.toUpperCase()}!\nWelcome, ${data.profile.first_name} ${data.profile.last_name}`);
            setButtonLoading(submitBtn, false);
        }, 800);

    } catch (err) {
        showFeedback(feedbackId, err.message, "error");
        setButtonLoading(submitBtn, false);
    }
}

/**
 * Register a new Student or Faculty user
 */
async function handleUserRegistration({
    email,
    password,
    schoolId,
    firstName,
    middleName,
    lastName,
    userType,
    feedbackId,
    submitBtn,
    onSuccess,
}) {
    hideFeedback(feedbackId);
    setButtonLoading(submitBtn, true);

    try {
        const payload = {
            email,
            password,
            school_id: schoolId,
            first_name: firstName,
            middle_name: middleName || null,
            last_name: lastName,
            user_type: userType,
        };

        const response = await fetch(`${API_BASE}/auth/register/user`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Registration failed. Please check your information.");
        }

        showFeedback(
            feedbackId,
            `Account created successfully for ${data.first_name}! You may now sign in with your credentials.`,
            "success"
        );
        setButtonLoading(submitBtn, false);

        if (typeof onSuccess === "function") {
            onSuccess(data);
        }
    } catch (err) {
        showFeedback(feedbackId, err.message, "error");
        setButtonLoading(submitBtn, false);
    }
}
