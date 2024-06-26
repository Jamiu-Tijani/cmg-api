import base64
import logging
import pyotp
from google.oauth2 import id_token
from google.auth.transport import requests
from django.shortcuts import redirect
import uuid
from decouple import config

from rest_framework.authtoken.models import Token

from django.contrib.auth import login, logout, user_logged_in, user_logged_out
from django.db.models import Q

from .utils.send_email import EmailManager
from .constants import ErrorMessages, SuccessMessages
from .helpers import validate_email_
from accounts.models import User
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .helpers import GenerateKey
from .models import Account, EmailToken

logger = logging.getLogger(__name__)


class AccountService:
    def __init__(self):
        self.user_model = Account
        self.token_model = Token

    def user_exists(self, email="", username=""):
        """
        Checks if a username or email exists.
        """
        return self.user_model.objects.filter(
            Q(email=email) | Q(username=username)
        ).exists()

    def create_user(self, request, **kwargs):
        password = kwargs.get("password")
        email = kwargs.get("email")
        username = str(uuid.uuid4())

        if not validate_email_(email):
            return dict(error=ErrorMessages.INVALID_EMAIL)
        if self.user_exists(email, username):
            return dict(error=ErrorMessages.ACCOUNT_ALREADY_EXISTS, status=409)

        # create the user and hash the password
        user = self.user_model.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        user = self.user_model.objects.get(email=email)
        user_profile = {
            x: user.__dict__[x] for x in user.__dict__.keys() if x[0] != "_"
        }
        user_profile["profile_picture"] = user.image_url
        data = {}
        data["email"] = user_profile["email"]
        data["first_name"] = user_profile["first_name"]
        data["last_name"] = user_profile["last_name"]
        data["profile_picture"] = user_profile["profile_picture"]
        # Automatically authenticate the user
        login(request, user)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        token, created = self.token_model.objects.get_or_create(user=user)

        user_data = {"token": token.key, "email": email}
        user_data.update(data)

        response = dict(success=SuccessMessages.ACCOUNT_CREATED)

        return dict(**response, data=user_data)

    def authenticate_user(self, request, **kwargs):
        username = kwargs.get("email")
        password = kwargs.get("password")

        user, user_exists = OTPServices.retrieve_user(username)
        if not user_exists:
            return dict(error=ErrorMessages.ACCOUNT_NOT_FOUND)
        if not user.check_password(password):
            return dict(error=ErrorMessages.INCORRECT_PASSWORD)

        login(request, user)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        token, created = self.token_model.objects.get_or_create(user=user)
        user = self.user_model.objects.get(email=request.user.email)
        user_profile = {
            x: user.__dict__[x] for x in user.__dict__.keys() if x[0] != "_"
        }
        user_profile["profile_picture"] = user.image_url
        data = {}
        data["email"] = user_profile["email"]
        data["first_name"] = user_profile["first_name"]
        data["last_name"] = user_profile["last_name"]
        data["profile_picture"] = user_profile["profile_picture"]
        data.update({"token": token.key})
        return dict(
            success=SuccessMessages.ACCOUNT_LOGIN_SUCCESSFUL, data=data, status=200
        )

    @staticmethod
    def user_logout(request):
        user = request.user
        Token.objects.get(user=user).delete()
        user_logged_out.send(sender=user.__class__, request=request, user=user)
        logout(request)
        return dict(success=SuccessMessages.ACCOUNT_LOGOUT_SUCCESSFUL)

    def update_user_profile(self, request, **kwargs):
        first_name = kwargs.get("first_name") if kwargs.get("first_name") else None
        last_name = kwargs.get("last_name") if kwargs.get("last_name") else None
        profile_picture = (
            kwargs.get("profile_picture") if kwargs.get("profile_picture") else None
        )
        user = self.user_model.objects.get(email=request.user.email)
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if profile_picture is not None:
            user.profile_picture = profile_picture
        user.save()
        user = self.user_model.objects.get(email=request.user.email)
        user_profile = {
            x: user.__dict__[x] for x in user.__dict__.keys() if x[0] != "_"
        }
        user_profile["profile_picture"] = user.image_url
        data = {}
        data["email"] = user_profile["email"]
        data["first_name"] = user_profile["first_name"]
        data["last_name"] = user_profile["last_name"]
        data["profile_picture"] = user_profile["profile_picture"]

        return dict(success="User Profile Updated Successfully", status=200, data=data)

    def delete_account(self, request):
        email = request.user.email
        user = self.user_model.objects.get(email=email)
        user.delete()
        return dict(success="User Account Deleted Successfully", status=200)

    def change_password(self, request, **kwargs):
        new_password = kwargs.get("new_password")
        old_password = kwargs.get("old_password")
        email = request.user.email
        user = self.user_model.objects.get(email=email)
        if not user.check_password(old_password):
            return dict(error="Incorrect Password", status=401)
        user.set_password(new_password)
        user.save()
        user = self.user_model.objects.get(email=request.user.email)
        user_profile = {
            x: user.__dict__[x] for x in user.__dict__.keys() if x[0] != "_"
        }
        user_profile["profile_picture"] = user.image_url
        data = {}
        data["email"] = user_profile["email"]
        data["first_name"] = user_profile["first_name"]
        data["last_name"] = user_profile["last_name"]
        data["profile_picture"] = user_profile["profile_picture"]
        return dict(
            success="User Account Password Changed Successfully", status=200, data=data
        )


class OTPServices:
    """
    An Email based otp service
    """

    @classmethod
    def retrieve_user(cls, username):
        user = None
        user_list = Account.objects.filter(Q(email=username) | Q(username=username))
        if user_list.exists():
            user = user_list.first()
        return user, user_list.exists()

    @classmethod
    def timed_email_otp(cls, email=None, verify_otp=False, submitted_otp=None):
        expiry_time = int(120) * 86_400  # convert to seconds
        if verify_otp:
            try:
                token_object = EmailToken.objects.get(email=email)
            except EmailToken.DoesNotExist:
                return dict(error=ErrorMessages.USER_ACCOUNT_NOT_FOUND)
        else:
            token_object, _ = EmailToken.objects.get_or_create(email=email)
        keygen = GenerateKey()
        key = base64.b32encode(keygen.return_value(email).encode())  # Key is generated
        otp = pyotp.TOTP(key, interval=expiry_time)  # TOTP Model for OTP is created
        if verify_otp:
            return otp.verify(submitted_otp), token_object
        return otp

    @classmethod
    def send_verification_email(cls, email):
        user, user_exists = cls.retrieve_user(email)
        if not user_exists:
            return dict(error=ErrorMessages.ACCOUNT_NOT_FOUND)
        username = user.username
        otp = cls.timed_email_otp(email)
        verification_link = f"?page=verify_email&email={email}&token={otp.now()}"

        EmailManager.send_email(
            email,
            "Email Verification",
            "email_verification.html",
            {"verification_link": verification_link, "username": username},
            "jimniz01@gmail.com",
        )
        return dict(success=SuccessMessages.ACCOUNT_PASSWORD_RESET_EMAIL_SENT)

    @classmethod
    def verify_email(cls, **kwargs):
        submitted_otp = kwargs.get("token")
        email = kwargs.get("email")

        # print(submitted_otp)

        user, user_exists = cls.retrieve_user(email)

        if not user_exists:
            return dict(error=ErrorMessages.ACCOUNT_NOT_FOUND)
        valid_otp, token_object = cls.timed_email_otp(
            user.email, verify_otp=True, submitted_otp=submitted_otp
        )

        if not valid_otp:
            return dict(error=ErrorMessages.INVALID_OTP)
        token_object.is_verified = True
        token_object.save()
        user.verified_email = True
        user.save()
        return dict(success=SuccessMessages.COMPLETE_EMAIL_VERIFICATION)

    @classmethod
    def send_password_reset_email(cls, email):
        user, user_exists = cls.retrieve_user(email)
        if not user_exists:
            return dict(error=ErrorMessages.USER_ACCOUNT_NOT_FOUND)
        otp = cls.timed_email_otp(email)
        password_reset_link = f"?page=reset_password&email={email}&token={otp.now()}"

        EmailManager.send_email(
            email,
            "Reset your password",
            "password_reset.html",
            {"password_reset_link": password_reset_link},
            "jimniz01@gmail.com",
        )
        return dict(success=SuccessMessages.ACCOUNT_PASSWORD_RESET_EMAIL_SENT)

    @classmethod
    def reset_password(cls, **kwargs):
        submitted_otp = kwargs.get("token")
        email = kwargs.get("email")
        new_password = kwargs.get("password")

        user, user_exists = cls.retrieve_user(email)
        if not user_exists:
            return dict(error=ErrorMessages.ACCOUNT_NOT_FOUND)

        valid_otp, token_object = cls.timed_email_otp(
            user.email, verify_otp=True, submitted_otp=submitted_otp
        )
        if not valid_otp:
            return dict(error=ErrorMessages.INVALID_OTP)
        token_object.is_verified = True
        token_object.save()
        user.set_password(new_password)
        user.save()
        return dict(success=SuccessMessages.ACCOUNT_PASSWORD_RESET_SUCCESSFUL)


class ExternalAuthServices:
    def __init__(self):
        self.user_model = Account
        self.token_model = Token

    def register_social_user(self, request, **kwargs):
        email = kwargs.get("email")
        provider = kwargs.get("provider")

        filtered_user_by_email = self.user_model.objects.filter(email=email)

        if filtered_user_by_email.exists():
            if provider == filtered_user_by_email[0].auth_provider:
                new_user = self.user_model.objects.get(email=email)

                registered_user = self.user_model.objects.get(email=email)
                registered_user.check_password(settings.SOCIAL_SECRET)
                token, created = self.token_model.objects.get_or_create(user=new_user)
                user = registered_user
                user_logged_in.send(sender=user.__class__, request=request, user=user)
                user_profile = {
                    x: user.__dict__[x] for x in user.__dict__.keys() if x[0] != "_"
                }
                user_profile["profile_picture"] = user.image_url
                data = {}
                data["email"] = user_profile["email"]
                data["first_name"] = user_profile["first_name"]
                data["last_name"] = user_profile["last_name"]
                data["profile_picture"] = user_profile["profile_picture"]
                data.update({"token": token.key})

                return dict(
                    success=SuccessMessages.ACCOUNT_LOGIN_SUCCESSFUL,
                    status=200,
                    data=data,
                )

            else:
                return dict(
                    error="Please continue your login using "
                    + filtered_user_by_email[0].auth_provider,
                    status=401,
                )

        else:
            user = {
                "username": email,
                "email": email,
                "password": settings.SOCIAL_SECRET,
            }
            user = self.user_model.objects.create_user(**user)
            user.is_active = True
            user.auth_provider = provider
            user.set_password(settings.SOCIAL_SECRET)
            user.save()
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            token, created = self.token_model.objects.get_or_create(user=user)
            user = registered_user
            user_profile = {
                x: user.__dict__[x] for x in user.__dict__.keys() if x[0] != "_"
            }
            user_profile["profile_picture"] = user.image_url
            data = {}
            data["email"] = user_profile["email"]
            data["first_name"] = user_profile["first_name"]
            data["last_name"] = user_profile["last_name"]
            data["profile_picture"] = user_profile["profile_picture"]
            data.update({"token": token.key})

            return dict(
                success=SuccessMessages.ACCOUNT_LOGIN_SUCCESSFUL, status=200, data=data
            )
