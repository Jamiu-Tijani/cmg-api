from django.db import transaction
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,AllowAny

from .serializers import inline_serializer
from .services import AccountService, OTPServices, ExternalAuthServices
from .mixins import CustomResponseMixin


class UserAuthenticationViewSet(CustomResponseMixin, viewsets.ViewSet):
    @action(detail=False, methods=["post"], url_path="create", permission_classes=[AllowAny])
    @transaction.atomic
    def create_user(self, request):
        serialized_data = inline_serializer(
            fields={
                "password": serializers.CharField(max_length=50),
                "email": serializers.CharField(max_length=50),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors


        response = AccountService().create_user(request=request, **serialized_data.validated_data)

        return self.response(response)

    @action(detail=False, methods=["post"], url_path="login",permission_classes=[AllowAny])
    def login_user(self, request):
        serialized_data = inline_serializer(
            fields={
                "email": serializers.CharField(max_length=50),
                "password": serializers.CharField(max_length=50),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = AccountService().authenticate_user(request, **serialized_data.validated_data)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="logout", permission_classes=[IsAuthenticated])
    def logout_user(self, request):
        response = AccountService().user_logout(request)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="verify-email-complete", permission_classes=[AllowAny])
    def verify_email(self, request):
        serialized_data = inline_serializer(
            fields={
                "email": serializers.CharField(max_length=50),
                "token": serializers.CharField(max_length=6,required=True),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = OTPServices.verify_email(**serialized_data.validated_data)
        return self.response(response)
    
    @action(detail=False, methods=["post"], url_path="verify-email",permission_classes=[AllowAny])
    def send_verification_email(self, request):
        serialized_data = inline_serializer(
            fields={
                "email": serializers.CharField(max_length=50),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = OTPServices.send_verification_email(**serialized_data.validated_data)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="reset-password", permission_classes=[AllowAny])
    def send_password_reset_email(self, request):
        serialized_data = inline_serializer(
            fields={
                "email": serializers.CharField(max_length=50),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = OTPServices.send_password_reset_email(**serialized_data.validated_data)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="reset-password-complete", permission_classes=[AllowAny])
    def reset_password(self, request):
        serialized_data = inline_serializer(
            fields={
                "email": serializers.CharField(max_length=50),
                "token": serializers.CharField(max_length=6),
                "password": serializers.CharField(max_length=50),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = OTPServices.reset_password(**serialized_data.validated_data)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="update-account-profile", permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        serialized_data = inline_serializer(
            fields={
                "first_name": serializers.CharField(max_length=50,required=False),
                "last_name": serializers.CharField(max_length=50,required=False),
                "profile_picture": serializers.ImageField(required=False),
            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)
        if errors:
            return errors

        response = AccountService().update_user_profile(request,**serialized_data.validated_data)
        return self.response(response)

    @action(detail=False, methods=["post"], url_path="external-social-auth", permission_classes=[AllowAny])
    def external_social_auth(self, request):
        serialized_data = inline_serializer(
            fields={
                "provider": serializers.CharField(max_length=20),         
                "email": serializers.CharField(max_length=50),
            },
            data=request.data)
        
        errors = self.validate_serializer(serialized_data)

        if errors:
            return errors

        response = ExternalAuthServices().register_social_user(request,**serialized_data.validated_data)
        return self.response(response)


    @action(detail=False, methods=["post"], url_path="delete", permission_classes=[IsAuthenticated])
    def delete_account(self, request):
        response = AccountService().delete_account(request)
        return self.response(response)
    @action(detail=False, methods=["post"], url_path="change-password", permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serialized_data = inline_serializer(
            fields={
                "old_password": serializers.CharField(max_length=30),         
                "new_password": serializers.CharField(max_length=30),         

            },
            data=request.data)
        errors = self.validate_serializer(serialized_data)

        if errors:
            return errors

        response = AccountService().change_password(request,**serialized_data.validated_data)
        return self.response(response)