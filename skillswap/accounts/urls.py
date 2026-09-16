from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("register/", views.register, name="register"),

    path(
        "login/",
        views.CustomLoginView.as_view(),
        name="login"
    ),

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password"
    ),

    path(
        "verify-otp/",
        views.verify_otp,
        name="verify_otp"
    ),

    path(
        "resend-otp/",
        views.resend_otp,
        name="resend_otp"
    ),

    path(
        "reset-password/",
        views.reset_password,
        name="reset_password"
    ),

    path(
        "logout-page/",
        views.logout_page,
        name="logout_page"
    ),

    path(
        "logout/",
        views.CustomLogoutView.as_view(),
        name="logout"
    ),


    path(
        "profile/",
        views.profile,
        name="profile"
    ),

    path(
        "profile/<int:user_id>/",
        views.profile,
        name="user_profile"
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile"
    ),
]