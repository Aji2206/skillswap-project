from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import Profile


@login_required
def match_users(request):

    current_profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    my_offered = (
        current_profile.skills_offered or ""
    ).lower()

    my_wanted = (
        current_profile.skills_wanted or ""
    ).lower()

    my_offer_list = [
        skill.strip()
        for skill in my_offered.split(",")
        if skill.strip()
    ]

    my_wanted_list = [
        skill.strip()
        for skill in my_wanted.split(",")
        if skill.strip()
    ]

    matches = []

    profiles = Profile.objects.exclude(
        user=request.user
    )

    for profile in profiles:

        offered = (
            profile.skills_offered or ""
        ).lower()

        wanted = (
            profile.skills_wanted or ""
        ).lower()

        offer_list = [
            skill.strip()
            for skill in offered.split(",")
            if skill.strip()
        ]

        wanted_list = [
            skill.strip()
            for skill in wanted.split(",")
            if skill.strip()
        ]

        percentage = 0

        # Perfect match

        common1 = set(my_wanted_list) & set(offer_list)

        common2 = set(my_offer_list) & set(wanted_list)

        percentage += len(common1) * 50
        percentage += len(common2) * 50

        percentage = min(percentage, 100)

        # Partial match

        if percentage == 0:

            common = set(my_offer_list) & set(offer_list)

            percentage = min(len(common) * 20, 80)

        if percentage > 0:

            matches.append({

                "user": profile.user,

                "profile": profile,

                "percentage": percentage,

                "common_offer": ", ".join(common1),

                "common_need": ", ".join(common2),

            })

    matches = sorted(

        matches,

        key=lambda x: x["percentage"],

        reverse=True

    )

    return render(

        request,

        "matching/matches.html",

        {

            "matches": matches

        }

    )