from django.db import transaction
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.serializers import inline_serializer
from accounts.mixins import CustomResponseMixin
from .services import InstagramService, TikTokService, TwitterService


class SocialsViewSet(CustomResponseMixin, viewsets.ViewSet):
    @action(
        detail=False,
        methods=["post"],
        url_path="instagram/stories",
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def stories(self, request):
        serialized_data = inline_serializer(
            fields={
                "username": serializers.CharField(max_length=500),
            },
            data=request.data,
        )
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = InstagramService().get_stories(**serialized_data.validated_data)

        return self.response(response)

    @action(
        detail=False,
        methods=["post"],
        url_path="instagram/stories-feeds",
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def stories_feeds(self, request):
        serialized_data = inline_serializer(
            fields={
                "username": serializers.CharField(max_length=500),
            },
            data=request.data,
        )
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = InstagramService().get_stories_feeds(**serialized_data.validated_data)

        return self.response(response)

    @action(
        detail=False,
        methods=["post"],
        url_path="instagram/recent-post",
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def recent_post(self, request):
        serialized_data = inline_serializer(
            fields={
                "username": serializers.CharField(max_length=500),
            },
            data=request.data,
        )
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = InstagramService().get_recent_post(**serialized_data.validated_data)

        return self.response(response)

    @action(
        detail=False,
        methods=["post"],
        url_path="tiktok/recent-post",
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def latest_feed(self, request):
        serialized_data = inline_serializer(
            fields={
                "username": serializers.CharField(max_length=500),
            },
            data=request.data,
        )
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = TikTokService.get_latest_feed(**serialized_data.validated_data)

        return self.response(response)

    @action(
        detail=False,
        methods=["post"],
        url_path="twitter/recent-post",
        permission_classes=[AllowAny],
    )
    @transaction.atomic
    def latest_feed(self, request):
        serialized_data = inline_serializer(
            fields={
                "username": serializers.CharField(max_length=500),
            },
            data=request.data,
        )
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = TwitterService.get_user_tweets(**serialized_data.validated_data)

        return self.response(response)