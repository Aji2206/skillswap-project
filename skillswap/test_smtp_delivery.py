import os
import sys
import socket
import smtplib
import django

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skillswap.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from decouple import config

def diagnose_email_delivery(test_recipient=None):
    print("=" * 70)
    print("SKILLSWAP REAL SMTP EMAIL DELIVERY DIAGNOSTIC TOOL")
    print("=" * 70)

    backend = getattr(settings, "EMAIL_BACKEND", "")
    host = getattr(settings, "EMAIL_HOST", "")
    port = getattr(settings, "EMAIL_PORT", 587)
    use_tls = getattr(settings, "EMAIL_USE_TLS", True)
    use_ssl = getattr(settings, "EMAIL_USE_SSL", False)
    user = getattr(settings, "EMAIL_HOST_USER", "")
    password = getattr(settings, "EMAIL_HOST_PASSWORD", "")
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "")
    timeout = getattr(settings, "EMAIL_TIMEOUT", 15)

    print(f"1. Email Backend:      {backend}")
    print(f"2. SMTP Host:          {host}")
    print(f"3. SMTP Port:          {port}")
    print(f"4. TLS Enabled:        {use_tls}")
    print(f"5. SSL Enabled:        {use_ssl}")
    print(f"6. Host User:          {user if user else '[NOT SET]'}")
    print(f"7. Host Password:      {'[CONFIGURED]' if password else '[NOT SET]'}")
    print(f"8. Default From:       {from_email}")
    print(f"9. Socket Timeout:     {timeout}s")
    print("-" * 70)

    # Step 1: Backend check
    if backend != "django.core.mail.backends.smtp.EmailBackend":
        print(f"[WARNING] EMAIL_BACKEND is set to '{backend}', not SMTP backend.")
        print("          Real emails will NOT be delivered over the network.")
        return False
    else:
        print("[PASS] EMAIL_BACKEND is correctly configured for real SMTP delivery.")

    # Step 2: Network connectivity check
    print(f"Testing TCP connection to {host}:{port}...")
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        print(f"[PASS] Successfully connected to {host}:{port} over the network.")
    except Exception as e:
        print(f"[FAIL] Network connection to {host}:{port} failed: {e}")
        return False

    # Step 3: SMTP Handshake & TLS
    print(f"Testing SMTP Handshake and TLS with {host}:{port}...")
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=timeout)
        else:
            server = smtplib.SMTP(host, port, timeout=timeout)
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
        print("[PASS] SMTP server responded and TLS encryption established.")
    except Exception as e:
        print(f"[FAIL] SMTP Handshake failed: {e}")
        return False

    # Step 4: Authentication check
    if not user or not password:
        print("\n" + "!" * 70)
        print("[ACTION REQUIRED] EMAIL_HOST_USER and/or EMAIL_HOST_PASSWORD are not set in .env")
        print("!" * 70)
        print("To deliver real OTP emails to real inboxes:")
        print("1. Open: skillswap/.env")
        print("2. Set EMAIL_HOST_USER=your_email@gmail.com")
        print("3. Generate a 16-character Google App Password at: https://myaccount.google.com/apppasswords")
        print("4. Set EMAIL_HOST_PASSWORD=your_16_char_password")
        print("5. Save .env and re-run this tool or restart the server.")
        server.quit()
        return False

    print(f"Authenticating as {user}...")
    try:
        server.login(user, password)
        print(f"[PASS] Authentication successful for {user}!")
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(f"[FAIL] SMTP Authentication failed: {e}")
        print("       Hint: If using Gmail, a standard Google password will NOT work.")
        print("       You must generate a 16-character App Password at: https://myaccount.google.com/apppasswords")
        server.quit()
        return False
    except Exception as e:
        print(f"[FAIL] Error during authentication: {e}")
        server.quit()
        return False

    # Step 5: Real test email delivery
    if test_recipient:
        print(f"\nSending real test email to {test_recipient}...")
        try:
            sent = send_mail(
                subject="SkillSwap Password Reset Verification [Delivery Test]",
                message=(
                    "SkillSwap\n\n"
                    "Password Reset Verification\n\n"
                    "Your 6-digit verification code is:\n\n"
                    "847291\n\n"
                    "This code expires in 5 minutes.\n\n"
                    "If you did not request a password reset, you can safely ignore this email.\n"
                ),
                from_email=from_email,
                recipient_list=[test_recipient],
                fail_silently=False,
            )
            if sent > 0:
                print(f"[SUCCESS] Real test email delivered to {test_recipient}! Check inbox / spam.")
                return True
            else:
                print(f"[FAIL] send_mail returned 0 messages delivered.")
                return False
        except Exception as e:
            print(f"[FAIL] send_mail raised an exception: {e}")
            return False

    return True

if __name__ == "__main__":
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    diagnose_email_delivery(recipient)
