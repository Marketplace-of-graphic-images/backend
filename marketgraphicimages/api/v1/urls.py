from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (auth_confirmation,
                          auth_signup_post,
                          get_token_post,
                          #UserViewSet
                          )
from users.views import UserViewSet


v1_router = DefaultRouter()
v1_router.register("users", UserViewSet)

auth_url = [
    path("signin/", get_token_post, name="signin"),
    path("signup/", auth_signup_post, name="signup"),
    path("signup/confirmation/", auth_confirmation, name="confirmation")
]

urlpatterns = [
    path("", include(v1_router.urls)),
    path("auth/", include("djoser.urls.jwt")),
    path("auth/", include(auth_url)),
    path("", include("djoser.urls")),
]
