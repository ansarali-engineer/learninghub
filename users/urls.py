from django.urls import path
from .views import user_list,register
urlpatterns = [
    # path('users',UserView.as_view()),
    path('users_list',user_list,name="users_list"),
    path('create_user',register,name="user_create")
]