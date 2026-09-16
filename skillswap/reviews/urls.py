from django.urls import path
from . import views

urlpatterns = [

    path(
        "<int:user_id>/",
        views.review_list,
        name="review_list"
    ),

    path(
        "add/<int:user_id>/",
        views.add_review,
        name="add_review"
    ),

]