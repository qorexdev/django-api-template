from django.urls import path
from app.users.views import MeView, ChangePasswordView

urlpatterns = [
    path("me/", MeView.as_view(), name="user-me"),
    path("me/change-password/", ChangePasswordView.as_view(), name="user-change-password"),
]
