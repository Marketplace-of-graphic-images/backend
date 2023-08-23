from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import auth_confirmation, auth_signup_post, get_token_post

v1_router = DefaultRouter()

auth_url = [
    path("signin/", get_token_post, name="signin"),
    path("signup/", auth_signup_post, name="signup"),
    path("signup/confirmation/", auth_confirmation, name="confirmation")
]

urlpatterns = [
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("auth/", include(auth_url)),
    path("", include(v1_router.urls)),
]
