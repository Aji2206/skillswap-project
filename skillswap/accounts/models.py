from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default="profile/default.png",
        blank=True,
        null=True
    )

    bio = models.TextField(blank=True)

    location = models.CharField(
        max_length=100,
        blank=True
    )

    skills_offered = models.TextField(blank=True)

    skills_wanted = models.TextField(blank=True)

    rating = models.FloatField(default=0)

    def get_skills_offered_list(self):
        if not self.skills_offered:
            return []
        return [s.strip() for s in self.skills_offered.split(",") if s.strip()]

    def get_skills_wanted_list(self):
        if not self.skills_wanted:
            return []
        return [s.strip() for s in self.skills_wanted.split(",") if s.strip()]

    def __str__(self):
        return self.user.username


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_otps"
    )
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def hash_otp(cls, user_id, raw_otp):
        from django.conf import settings
        salt = getattr(settings, "SECRET_KEY", "default-salt")
        import hashlib
        return hashlib.sha256(f"{user_id}:{raw_otp}:{salt}".encode("utf-8")).hexdigest()

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def can_attempt(self):
        return self.attempts < 5 and not self.is_used and not self.is_expired()

    def verify_otp(self, raw_otp):
        if not self.can_attempt():
            return False
        expected_hash = self.hash_otp(self.user_id, raw_otp)
        if self.otp_hash == expected_hash:
            return True
        self.attempts += 1
        self.save(update_fields=["attempts"])
        return False

    def __str__(self):
        return f"PasswordResetOTP for {self.user.username} ({'Used' if self.is_used else 'Pending'})"