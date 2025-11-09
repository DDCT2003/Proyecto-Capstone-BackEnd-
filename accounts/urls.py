from django.urls import path
from .views import RegisterView, MeView, UpdateMeView, ChangePasswordView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("me/update/",       UpdateMeView.as_view(), name="me-update"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]