from django.urls import path, include
from api.views import RegisterAPI, LoginAPI, UserAPI, LogoutAPI

urlpatterns = [
    path('api/auth/login', LoginAPI.as_view()),
    path('api/auth/register', RegisterAPI.as_view()),
    path('api/auth/user', UserAPI.as_view()),
    path('api/auth/logout', LogoutAPI.as_view()),
]