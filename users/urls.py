from django.urls import path
from .views import login, register, user_list

urlpatterns = [
    path("login", login, name="user_login"),
    path("users_list", user_list, name="users_list"),
    path("create_user", register, name="user_create"),
]