from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )

    reviewee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("reviewer", "reviewee")

    def __str__(self):
        return f"{self.reviewer.username} → {self.reviewee.username}"