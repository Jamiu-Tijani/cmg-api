from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .viewsets import UserAuthenticationViewSet

router = DefaultRouter()
router.register(r"auth-user", UserAuthenticationViewSet, basename="auth_user")

urlpatterns = [
    path("", include(router.urls)),
]
