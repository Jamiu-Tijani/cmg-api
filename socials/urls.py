from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .viewsets import SocialsViewSet

router = DefaultRouter()
router.register(r"get-socials", SocialsViewSet, basename="get_socials")

urlpatterns = [
    path("", include(router.urls)),]