from django.contrib import admin
from .models import Skill, SkillRequest


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "user",
        "created_at",
    )

    list_filter = (
        "category",
    )

    search_fields = (
        "title",
        "description",
        "user__username",
    )


@admin.register(SkillRequest)
class SkillRequestAdmin(admin.ModelAdmin):

    list_display = (
        "requester_name",
        "requester_email",
        "skill",
        "created_at",
    )

    search_fields = (
        "requester_name",
        "requester_email",
        "skill__title",
    )