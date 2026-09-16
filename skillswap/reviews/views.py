from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg

from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, user_id):

    reviewee = get_object_or_404(
        User,
        id=user_id
    )

    if reviewee == request.user:
        return redirect("review_list", user_id=user_id)

    if Review.objects.filter(
        reviewer=request.user,
        reviewee=reviewee
    ).exists():

        return redirect(
            "review_list",
            user_id=user_id
        )

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.reviewer = request.user
            review.reviewee = reviewee

            review.save()

            avg = Review.objects.filter(reviewee=reviewee).aggregate(Avg("rating"))["rating__avg"]
            if hasattr(reviewee, "profile") and avg is not None:
                reviewee.profile.rating = round(avg, 1)
                reviewee.profile.save()

            return redirect(
                "review_list",
                user_id=user_id
            )

    else:

        form = ReviewForm()

    return render(

        request,

        "reviews/add_review.html",

        {

            "form": form,

            "reviewee": reviewee,

        }

    )


def review_list(request, user_id):

    reviewee = get_object_or_404(
        User,
        id=user_id
    )

    reviews = Review.objects.filter(
        reviewee=reviewee
    )

    average = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    return render(

        request,

        "reviews/review_list.html",

        {

            "reviewee": reviewee,

            "reviews": reviews,

            "average": average or 0,

        }

    )