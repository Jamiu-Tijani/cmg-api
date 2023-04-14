from rest_framework import serializers
from django.conf import settings
from rest_framework import serializers
from accounts.social_lib import google
from .services import ExternalAuthServices
from rest_framework.exceptions import AuthenticationFailed


def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    """
    A one-time use serializer
    Sample usage:
        serialized_data = inline_serializer(
            fields={
                "username": serializers.CharField(max_length=50),
                "password": serializers.CharField(max_length=50),
                "email": serializers.CharField(max_length=50),
            },
            data=request.data)
    """
    serializer_class = create_serializer_class(name="inline_serializer", fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data["sub"]
        except:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )
        print(user_data["aud"])
        if user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("oops, who are you?")

        user_id = user_data["sub"]
        email = user_data["email"]
        name = user_data["name"]
        provider = "google"

        return ExternalServices.register_social_user(
            provider=provider, user_id=user_id, email=email, name=name
        )
