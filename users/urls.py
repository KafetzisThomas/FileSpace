from django.urls import path
from django.contrib.auth import views as auth_views
from .views import RegisterView, AccountView

app_name = "users"
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("account/", AccountView.as_view(template_name="users/account.html"), name="account"),
    path("logout/", auth_views.LogoutView.as_view(next_page="users:login"), name="logout"),
]
