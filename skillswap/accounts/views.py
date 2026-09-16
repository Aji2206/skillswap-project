from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import timedelta
import smtplib
import socket
import logging
import secrets
import time

from .forms import RegisterForm, ProfileForm
from .models import Profile, PasswordResetOTP

logger = logging.getLogger("accounts.email")


# ---------------- HOME ----------------

@ensure_csrf_cookie
def home(request):
    from skills.models import Skill
    featured_skills = Skill.objects.select_related("user", "user__profile").order_by("-created_at")[:6]
    total_skills = Skill.objects.count()
    total_members = User.objects.count()
    return render(
        request,
        "index.html",
        {
            "featured_skills": featured_skills,
            "total_skills": total_skills,
            "total_members": total_members,
        },
    )


# ---------------- REGISTER ----------------

@ensure_csrf_cookie
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to SkillSwap, {user.username}! Your account has been created.")
            return redirect("dashboard")
        else:
            messages.error(request, "Please check the errors below and try again.")
    else:
        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form
        }
    )


# ---------------- CSRF FAILURE HANDLER ----------------

def csrf_failure(request, reason=""):
    if request.user.is_authenticated:
        messages.info(request, "Your session was refreshed. Welcome back to your dashboard!")
        return redirect("dashboard")
    return render(
        request,
        "csrf_error.html",
        {"reason": reason},
        status=403
    )


# ---------------- LOGIN ----------------

class CustomLoginView(LoginView):

    template_name = "login.html"

    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard")


# ---------------- LOGOUT PAGE ----------------

def logout_page(request):
    return render(request, "logout.html")


# ---------------- LOGOUT ----------------

class CustomLogoutView(LogoutView):

    http_method_names = ["get", "post"]

    next_page = reverse_lazy("home")


# ---------------- DASHBOARD ----------------

@login_required
def dashboard(request):
    return redirect("dashboard")

# ---------------- PROFILE ----------------

@login_required
def profile(request, user_id=None):
    if user_id:
        target_user = get_object_or_404(User, id=user_id)
    else:
        target_user = request.user

    user_profile, created = Profile.objects.get_or_create(
        user=target_user
    )

    if request.method == "POST" and "profile_picture" in request.FILES:
        if target_user == request.user:
            user_profile.profile_picture = request.FILES["profile_picture"]
            user_profile.save()
            messages.success(request, "Your profile picture has been updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "You can only edit your own profile.")

    user_skills = target_user.skills.all()

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": user_profile,
            "target_user": target_user,
            "user_skills": user_skills,
            "is_own_profile": (target_user == request.user),
        }
    )


# ---------------- EDIT PROFILE ----------------

@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            return redirect("profile")

    else:

        form = ProfileForm(instance=profile)

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
            "profile": profile
        }
    )


# ---------------- FORGOT PASSWORD & OTP SYSTEM ----------------

def mask_email(email):
    """Mask email for display, e.g., aj***@gmail.com"""
    if not email or "@" not in email:
        return email
    try:
        user_part, domain = email.split("@", 1)
        if len(user_part) <= 2:
            masked_user = user_part[0] + "*"
        else:
            masked_user = user_part[:2] + "*" * (len(user_part) - 2)
        return f"{masked_user}@{domain}"
    except Exception:
        return email


def send_otp_email(user, raw_otp):
    """
    Delivers a 6-digit OTP to the registered user's email address.
    Uses configured Django EMAIL_BACKEND.
    Returns: (success: bool, error_message: str or None)
    """
    if not user.email:
        logger.error("User %s (ID %s) has no email address registered", user.username, user.id)
        return False, "This account does not have a registered email address."

    subject = "SkillSwap Password Reset Verification"
    message = (
        "SkillSwap\n\n"
        "Password Reset Verification\n\n"
        "Your 6-digit verification code is:\n\n"
        f"{raw_otp}\n\n"
        "This code expires in 5 minutes.\n\n"
        "If you did not request a password reset, you can safely ignore this email.\n"
    )

    # Pre-flight check for SMTP credentials if SMTP backend is configured
    email_backend = getattr(settings, "EMAIL_BACKEND", "")
    email_user = getattr(settings, "EMAIL_HOST_USER", "")
    email_pass = getattr(settings, "EMAIL_HOST_PASSWORD", "")
    if "smtp" in email_backend.lower() and (not email_user or not email_pass):
        logger.error("SMTP delivery aborted: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are not configured in .env")
        return False, "SMTP credentials are not configured in .env. Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD."

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or "SkillSwap <noreply@skillswap.local>"

    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
        )
        if sent > 0:
            logger.info("Password reset OTP successfully sent to user %s (%s)", user.username, user.email)
            return True, None
        else:
            logger.error("send_mail returned 0 delivered messages for user %s", user.username)
            return False, "Email delivery provider returned 0 messages delivered."
    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP Authentication Failed for user %s: %s", user.username, str(e))
        return False, "SMTP authentication failed. Please verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env file."
    except smtplib.SMTPSenderRefused as e:
        logger.error("SMTP Sender Refused for user %s: %s", user.username, str(e))
        if e.smtp_code == 530 or "Authentication Required" in str(e):
            return False, "SMTP Authentication Required: Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env file."
        return False, "Email sender was refused by SMTP server. Please verify DEFAULT_FROM_EMAIL in .env."
    except smtplib.SMTPRecipientsRefused as e:
        logger.error("SMTP Recipient Refused for user %s (%s): %s", user.username, user.email, str(e))
        return False, f"Email address '{user.email}' was rejected by the mail provider."
    except (smtplib.SMTPConnectError, socket.timeout, socket.error) as e:
        logger.error("SMTP Connection Failed for user %s: %s", user.username, str(e))
        return False, "Unable to connect to the email server. Please verify your internet connection and SMTP host/port configuration."
    except smtplib.SMTPServerDisconnected as e:
        logger.error("SMTP Server Disconnected unexpectedly for user %s: %s", user.username, str(e))
        return False, "Email server disconnected unexpectedly. Please try again."
    except smtplib.SMTPException as e:
        logger.error("SMTP Exception occurred for user %s: %s", user.username, str(e))
        return False, f"SMTP delivery error: {type(e).__name__}."
    except Exception as e:
        logger.error("Unexpected error delivering OTP email to user %s: %s", user.username, str(e))
        return False, f"Email delivery failed: {type(e).__name__}."


@ensure_csrf_cookie
def forgot_password(request):
    """Step 1: User enters email, OTP is generated and emailed."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, "accounts/forgot_password.html")

        if "@" not in email or "." not in email.split("@")[-1]:
            messages.error(request, "Please enter a valid email address.")
            return render(request, "accounts/forgot_password.html", {"email": email})

        # Cooldown enforcement
        last_sent = request.session.get("otp_last_sent", 0)
        cooldown_left = int(60 - (time.time() - last_sent))
        if cooldown_left > 0:
            messages.warning(request, f"Please wait {cooldown_left} second(s) before requesting another code.")
            return render(request, "accounts/forgot_password.html", {"email": email, "cooldown": cooldown_left})

        user = User.objects.filter(email__iexact=email).first()

        if user:
            # Generate 6-digit cryptographic OTP
            raw_otp = f"{secrets.randbelow(900000) + 100000:06d}"
            otp_hash = PasswordResetOTP.hash_otp(user.id, raw_otp)
            expires_at = timezone.now() + timedelta(minutes=5)

            # Create pending OTP record
            otp_record = PasswordResetOTP.objects.create(
                user=user,
                otp_hash=otp_hash,
                expires_at=expires_at,
                attempts=0,
                is_used=False,
            )

            # Attempt REAL delivery
            delivered, error_msg = send_otp_email(user, raw_otp)

            if not delivered:
                # Mark failed record as used so no ghost OTP remains
                otp_record.is_used = True
                otp_record.save()
                messages.error(
                    request,
                    f"Email delivery failed: {error_msg}"
                )
                return render(request, "accounts/forgot_password.html", {"email": email})

            # Invalidate any prior unused OTPs only after delivery succeeded
            PasswordResetOTP.objects.filter(user=user, is_used=False).exclude(id=otp_record.id).update(is_used=True)

            request.session["pwd_reset_email"] = email
            request.session["otp_last_sent"] = time.time()
            messages.success(
                request,
                "A 6-digit verification code has been sent to your registered email. Please check your inbox."
            )
            return redirect("verify_otp")
        else:
            # User enumeration protection: show generic message and redirect to verify_otp
            request.session["pwd_reset_email"] = email
            request.session["otp_last_sent"] = time.time()
            messages.success(
                request,
                "If an account with that email exists, an OTP has been sent. Please check your inbox."
            )
            return redirect("verify_otp")

    return render(request, "accounts/forgot_password.html")


@ensure_csrf_cookie
def verify_otp(request):
    """Step 2: User verifies the 6-digit OTP."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    email = request.session.get("pwd_reset_email")
    if not email:
        messages.info(request, "Please enter your email to start the password reset process.")
        return redirect("forgot_password")

    masked_email = mask_email(email)
    last_sent = request.session.get("otp_last_sent", 0)
    cooldown_left = max(0, int(60 - (time.time() - last_sent)))

    if request.method == "POST":
        raw_otp = request.POST.get("otp", "").strip()
        if not raw_otp:
            messages.error(request, "Please enter the 6-digit verification code.")
            return render(
                request,
                "accounts/verify_otp.html",
                {"masked_email": masked_email, "cooldown": cooldown_left}
            )

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.error(request, "Invalid or expired verification code.")
            return render(
                request,
                "accounts/verify_otp.html",
                {"masked_email": masked_email, "cooldown": cooldown_left}
            )

        otp_record = (
            PasswordResetOTP.objects.filter(user=user, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp_record or otp_record.is_expired():
            messages.error(request, "This verification code has expired. Please request a new one.")
            return render(
                request,
                "accounts/verify_otp.html",
                {"masked_email": masked_email, "cooldown": cooldown_left}
            )

        if not otp_record.can_attempt():
            otp_record.is_used = True
            otp_record.save()
            messages.error(request, "Maximum verification attempts exceeded. Please request a new code.")
            return redirect("forgot_password")

        if otp_record.verify_otp(raw_otp):
            # Success! Mark OTP as used and generate single-use reset token
            token = secrets.token_urlsafe(32)
            otp_record.reset_token = token
            otp_record.is_used = True
            otp_record.save()

            request.session["pwd_reset_token"] = token
            messages.success(request, "Verification code confirmed. Please set your new password.")
            return redirect("reset_password")
        else:
            remaining = 5 - otp_record.attempts
            if remaining > 0:
                messages.error(
                    request,
                    f"Invalid verification code. You have {remaining} attempt(s) remaining."
                )
                return render(
                    request,
                    "accounts/verify_otp.html",
                    {"masked_email": masked_email, "cooldown": cooldown_left}
                )
            else:
                otp_record.is_used = True
                otp_record.save()
                messages.error(
                    request,
                    "Too many failed attempts. This code has been invalidated. Please request a new one."
                )
                return redirect("forgot_password")

    return render(
        request,
        "accounts/verify_otp.html",
        {"masked_email": masked_email, "cooldown": cooldown_left}
    )


def resend_otp(request):
    """Resend a new OTP with 60-second cooldown enforcement."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    email = request.session.get("pwd_reset_email")
    if not email:
        messages.info(request, "Please enter your email to request a reset code.")
        return redirect("forgot_password")

    last_sent = request.session.get("otp_last_sent", 0)
    cooldown_left = int(60 - (time.time() - last_sent))
    if cooldown_left > 0:
        messages.warning(request, f"Please wait {cooldown_left} second(s) before requesting a new code.")
        return redirect("verify_otp")

    user = User.objects.filter(email__iexact=email).first()

    if user:
        raw_otp = f"{secrets.randbelow(900000) + 100000:06d}"
        otp_hash = PasswordResetOTP.hash_otp(user.id, raw_otp)
        expires_at = timezone.now() + timedelta(minutes=5)

        otp_record = PasswordResetOTP.objects.create(
            user=user,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0,
            is_used=False,
        )

        delivered, error_msg = send_otp_email(user, raw_otp)
        if not delivered:
            otp_record.is_used = True
            otp_record.save()
            messages.error(request, f"Unable to resend verification code: {error_msg}")
            return redirect("verify_otp")

        # Invalidate previous OTPs only after delivery succeeded
        PasswordResetOTP.objects.filter(user=user, is_used=False).exclude(id=otp_record.id).update(is_used=True)
        request.session["otp_last_sent"] = time.time()
        messages.success(request, "A new verification code has been sent to your email.")
    else:
        request.session["otp_last_sent"] = time.time()
        messages.success(request, "A new verification code has been sent to your email.")

    return redirect("verify_otp")


@ensure_csrf_cookie
def reset_password(request):
    """Step 3: User enters new password after verified OTP session token."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    email = request.session.get("pwd_reset_email")
    token = request.session.get("pwd_reset_token")

    if not email or not token:
        messages.error(request, "Unauthorized session or expired verification. Please request a new code.")
        return redirect("forgot_password")

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        messages.error(request, "Invalid reset session. Please request a new code.")
        return redirect("forgot_password")

    # Verify that the session token matches the database reset_token
    otp_record = (
        PasswordResetOTP.objects.filter(user=user, reset_token=token, is_used=True)
        .order_by("-created_at")
        .first()
    )
    if not otp_record:
        messages.error(request, "Reset authorization has expired or is invalid. Please start over.")
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if not new_password or not confirm_password:
            messages.error(request, "Both password fields are required.")
            return render(request, "accounts/reset_password.html")

        if new_password != confirm_password:
            messages.error(request, "The passwords do not match. Please try again.")
            return render(request, "accounts/reset_password.html")

        # Validate password strength against Django's configured auth validators
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, "accounts/reset_password.html")

        # Update password
        user.set_password(new_password)
        user.save()

        # Invalidate reset token and clear session
        otp_record.reset_token = ""
        otp_record.save()

        request.session.pop("pwd_reset_email", None)
        request.session.pop("pwd_reset_token", None)
        request.session.pop("otp_last_sent", None)

        messages.success(request, "Your password has been reset successfully! You can now log in with your new password.")
        return redirect("login")

    return render(request, "accounts/reset_password.html")