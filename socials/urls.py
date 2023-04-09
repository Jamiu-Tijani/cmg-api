from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .viewsets import UserAuthenticationViewSet

router = DefaultRouter()
router.register(r"get-socials", UserAuthenticationViewSet, basename="get_socials")

urlpatterns = [
    path("", include(router.urls)),]