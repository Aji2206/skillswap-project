from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):

    CATEGORY_CHOICES = [

        ("Programming", "Programming"),
        ("Design", "Design"),
        ("Music", "Music"),
        ("Sports", "Sports"),
        ("Language", "Language"),
        ("Other", "Other"),

    ]

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE,

        related_name="skills"

    )

    title = models.CharField(
        max_length=100
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class SkillRequest(models.Model):

    skill = models.ForeignKey(

        Skill,

        on_delete=models.CASCADE,

        related_name="requests"

    )

    requester_name = models.CharField(
        max_length=100
    )

    requester_email = models.EmailField()

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.requester_name} → {self.skill.title}"