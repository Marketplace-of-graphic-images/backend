from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .schemas import schema_view
from .views import (
    ImageViewSet,
    TagViewSet,
    UserViewSet,
    ProfileViewSet,
    auth_confirmation,
    auth_signup_post,
    get_token_post,
    sign_out,
)

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)
v1_router.register('image', ImageViewSet, basename='image')
v1_router.register('tags', TagViewSet, basename='tags')

auth_url = [
    path('signin/', get_token_post, name='signin'),
    path('signup/', auth_signup_post, name='signup'),
    path('signup-confirmation/', auth_confirmation, name='confirmation'),
    path('signout/', sign_out, name='signout'),
]

profile_urls = [
    path(r'<int:pk>/', ProfileViewSet.as_view(
        {'get': 'retrieve'}), name='user-detail'),
]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include(auth_url)),
    path('auth/social/', include('djoser.social.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('profile/', include(profile_urls)),
    path('', include('djoser.urls')),
    path(
        'swagger<format>/',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
