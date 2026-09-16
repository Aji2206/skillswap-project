from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q

from accounts.models import Profile
from skills.models import Skill, SkillRequest
from messaging.models import Message
from reviews.models import Review


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    my_skills = Skill.objects.filter(user=request.user).prefetch_related("requests")
    received_requests = SkillRequest.objects.filter(skill__user=request.user).select_related("skill").order_by("-created_at")[:6]
    
    messages_count = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).count()

    reviews = Review.objects.filter(reviewee=request.user)
    reviews_count = reviews.count()
    peers_count = Profile.objects.exclude(user=request.user).count()

    context = {
        "profile": profile,
        "my_skills": my_skills,
        "received_requests": received_requests,
        "skills_count": my_skills.count(),
        "messages_count": messages_count,
        "reviews_count": reviews_count,
        "peers_count": peers_count,
    }
    return render(
        request,
        "dashboard/dashboard.html",
        context
    )