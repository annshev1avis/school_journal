import django.contrib.auth.views as auth_view
from django.urls import path


app_name = "users"

urlpatterns = [
    path(
        "login/",
        auth_view.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_view.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
]
