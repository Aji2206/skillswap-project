// ==================================================
// SKILLSWAP — PRODUCTION JAVASCRIPT (HUMAN-DESIGNED)
// ==================================================

document.addEventListener("DOMContentLoaded", () => {
    // --------------------------------------------------
    // 1. Mobile Menu Drawer Toggle
    // --------------------------------------------------
    const menuBtn = document.getElementById("menu-btn");
    const navbar = document.getElementById("mainNavbar");

    if (menuBtn && navbar) {
        const toggleMenu = (open) => {
            const isActive = open !== undefined ? open : !navbar.classList.contains("active");
            navbar.classList.toggle("active", isActive);
            const icon = menuBtn.querySelector("i") || menuBtn;
            if (isActive) {
                icon.className = "fa-solid fa-xmark";
                document.body.style.overflow = "hidden";
            } else {
                icon.className = "fa-solid fa-bars";
                document.body.style.overflow = "";
            }
        };

        menuBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleMenu();
        });

        // Close when clicking nav links
        navbar.querySelectorAll("a").forEach(link => {
            link.addEventListener("click", () => toggleMenu(false));
        });

        // Close when clicking outside
        document.addEventListener("click", (e) => {
            if (navbar.classList.contains("active") && !navbar.contains(e.target) && !menuBtn.contains(e.target)) {
                toggleMenu(false);
            }
        });

        // Close on ESC
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && navbar.classList.contains("active")) {
                toggleMenu(false);
            }
        });
    }

    // --------------------------------------------------
    // 2. User Profile Dropdown in Header
    // --------------------------------------------------
    const userDropdownBtn = document.getElementById("userDropdownBtn");
    const userDropdownMenu = document.getElementById("userDropdownMenu");

    if (userDropdownBtn && userDropdownMenu) {
        userDropdownBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            const isOpen = userDropdownMenu.classList.contains("show");
            userDropdownMenu.classList.toggle("show", !isOpen);
            userDropdownBtn.setAttribute("aria-expanded", !isOpen);
        });

        document.addEventListener("click", (e) => {
            if (!userDropdownBtn.contains(e.target) && !userDropdownMenu.contains(e.target)) {
                userDropdownMenu.classList.remove("show");
                userDropdownBtn.setAttribute("aria-expanded", "false");
            }
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                userDropdownMenu.classList.remove("show");
                userDropdownBtn.setAttribute("aria-expanded", "false");
            }
        });
    }

    // --------------------------------------------------
    // 3. Header Shadow Elevation on Scroll
    // --------------------------------------------------
    const header = document.querySelector(".header");
    if (header) {
        const updateHeaderElevation = () => {
            if (window.scrollY > 15) {
                header.style.boxShadow = "0 4px 16px rgba(15, 23, 42, 0.06)";
                header.style.borderBottomColor = "var(--border-strong)";
            } else {
                header.style.boxShadow = "none";
                header.style.borderBottomColor = "rgba(226, 232, 240, 0.85)";
            }
        };
        window.addEventListener("scroll", updateHeaderElevation, { passive: true });
        updateHeaderElevation();
    }

    // --------------------------------------------------
    // 4. Back To Top Button
    // --------------------------------------------------
    const topBtn = document.getElementById("topBtn");
    if (topBtn) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 360) {
                topBtn.style.display = "flex";
            } else {
                topBtn.style.display = "none";
            }
        }, { passive: true });

        topBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // --------------------------------------------------
    // 5. Toast Notifications (Auto-Dismiss & Close)
    // --------------------------------------------------
    const toastMessages = document.querySelectorAll(".toast-message");
    toastMessages.forEach(toast => {
        const closeBtn = toast.querySelector(".toast-close");
        const dismissToast = () => {
            toast.style.transition = "opacity 0.22s ease, transform 0.22s ease";
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-8px)";
            setTimeout(() => toast.remove(), 240);
        };

        if (closeBtn) {
            closeBtn.addEventListener("click", dismissToast);
        }
        setTimeout(dismissToast, 4500);
    });

    // --------------------------------------------------
    // 6. Chat Scroll to Bottom
    // --------------------------------------------------
    const chatBody = document.querySelector(".chat-body");
    if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // --------------------------------------------------
    // 7. Interactive Star Rating with Dynamic Feedback
    // --------------------------------------------------
    const ratingInputs = document.querySelectorAll(".star-rating input[type='radio']");
    const ratingFeedback = document.getElementById("ratingFeedback");
    const ratingLabels = [
        "1 / 5 - Needs Improvement",
        "2 / 5 - Fair Exchange",
        "3 / 5 - Good Session",
        "4 / 5 - Very Good & Helpful",
        "5 / 5 - Outstanding Collaboration"
    ];

    if (ratingInputs.length > 0) {
        ratingInputs.forEach(input => {
            input.addEventListener("change", () => {
                const val = parseInt(input.value, 10);
                if (ratingFeedback && val >= 1 && val <= 5) {
                    ratingFeedback.innerText = ratingLabels[val - 1];
                }
            });
        });
    }

    // --------------------------------------------------
    // 8. Password Visibility Toggle
    // --------------------------------------------------
    document.querySelectorAll(".toggle-password").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const targetInput = document.getElementById(targetId);
            if (targetInput) {
                const isPassword = targetInput.getAttribute("type") === "password";
                targetInput.setAttribute("type", isPassword ? "text" : "password");
                const icon = btn.querySelector("i");
                if (icon) {
                    icon.className = isPassword ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
                }
            }
        });
    });

    // --------------------------------------------------
    // 9. Quick Trending Skill Search Tags
    // --------------------------------------------------
    const heroSearchInput = document.getElementById("heroSearchInput");
    const heroSearchForm = document.getElementById("heroSearchForm");
    const quickSkillTags = document.querySelectorAll(".quick-skill-tag");

    if (heroSearchInput && quickSkillTags.length > 0) {
        quickSkillTags.forEach(tag => {
            tag.addEventListener("click", () => {
                const query = tag.getAttribute("data-query") || tag.innerText.trim();
                heroSearchInput.value = query;
                heroSearchInput.focus();
                if (heroSearchForm) {
                    heroSearchForm.submit();
                }
            });
        });
    }

    // --------------------------------------------------
    // 10. Form Submit Prevention & Visual Feedback
    // --------------------------------------------------
    document.querySelectorAll("form").forEach(form => {
        if (form.method && form.method.toUpperCase() === "POST") {
            form.addEventListener("submit", (e) => {
                const submitBtn = form.querySelector("button[type='submit']");
                if (submitBtn && !submitBtn.disabled) {
                    setTimeout(() => {
                        submitBtn.disabled = true;
                        submitBtn.style.opacity = "0.8";
                        const icon = submitBtn.querySelector("i");
                        if (icon) {
                            icon.className = "fa-solid fa-spinner fa-spin";
                        }
                    }, 40);
                }
            });
        }
    });
});

// BFCache page restoration
window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
        window.location.reload();
    }
});
