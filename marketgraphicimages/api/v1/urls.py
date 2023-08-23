from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

v1_router = DefaultRouter()
v1_router.register("users", UserViewSet)


urlpatterns = [
    path("", include(v1_router.urls)),
    path('auth/social/', include('djoser.social.urls')),
    path("auth/", include("djoser.urls.jwt")),
    path("", include("djoser.urls")),
]
