from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.inbox,
        name="messages"
    ),

    path(
        "inbox/",
        views.inbox,
        name="inbox"
    ),

    path(
        "chat/<int:user_id>/",
        views.chat,
        name="chat"
    ),

]