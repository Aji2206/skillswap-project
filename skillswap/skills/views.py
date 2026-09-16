from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Skill
from .forms import SkillForm, SkillRequestForm


def skill_list(request):
    category = request.GET.get("category", "").strip()
    skills = Skill.objects.select_related("user", "user__profile").order_by("-created_at")

    if category and category.lower() != "all":
        skills = skills.filter(category__iexact=category)

    return render(
        request,
        "skills/skill_list.html",
        {
            "skills": skills,
            "selected_category": category or "All",
        },
    )


@login_required
def add_skill(request):

    form = SkillForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            skill = form.save(
                commit=False
            )

            skill.user = request.user

            skill.save()

            return redirect(
                "skill_list"
            )

    return render(
        request,
        "skills/add_skill.html",
        {
            "form": form
        }
    )


@login_required
def edit_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, f"Skill '{skill.title}' updated successfully!")
            return redirect("dashboard")
    else:
        form = SkillForm(instance=skill)

    return render(
        request,
        "skills/edit_skill.html",
        {
            "form": form,
            "skill": skill,
        }
    )


@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == "POST":
        title = skill.title
        skill.delete()
        messages.success(request, f"Skill '{title}' was deleted.")
        return redirect("dashboard")

    return redirect("dashboard")


def search_skill(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    skills = Skill.objects.none()
    matching_members = []

    if query:
        skills = Skill.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__icontains=query)
        ).select_related("user")

        from accounts.models import Profile
        profiles_qs = Profile.objects.filter(
            Q(skills_offered__icontains=query) | Q(skills_wanted__icontains=query)
        ).select_related("user")
        if request.user.is_authenticated:
            profiles_qs = profiles_qs.exclude(user=request.user)
        matching_members = list(profiles_qs)

    return render(
        request,
        "skills/search_skill.html",
        {
            "query": query,
            "skills": skills,
            "matching_members": matching_members,
        }
    )


@login_required
def request_skill(request, skill_id):

    skill = get_object_or_404(
        Skill,
        id=skill_id
    )

    if request.method == "POST":

        form = SkillRequestForm(
            request.POST
        )

        if form.is_valid():

            request_skill = form.save(
                commit=False
            )

            request_skill.skill = skill

            request_skill.save()

            return redirect(
                "skill_list"
            )

    else:

        form = SkillRequestForm()

    return render(

        request,

        "skills/request_skill.html",

        {

            "skill": skill,

            "form": form,

        }

    )