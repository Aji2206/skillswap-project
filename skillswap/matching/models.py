from django.db import models
from django.contrib.auth.models import User


class Match(models.Model):

    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="matches_sent"
    )

    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="matches_received"
    )

    matched_skill = models.CharField(
        max_length=100,
        blank=True
    )

    percentage = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"