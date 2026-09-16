from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.match_users,
        name="matches"
    ),

]