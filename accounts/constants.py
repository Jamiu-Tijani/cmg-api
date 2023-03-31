from django.utils.translation import ugettext_lazy as _


class ErrorMessages:
    PARAMETER_ERROR = _('Check if all required parameters are filled')
    INVALID_OTP = _('You have entered an invalid otp, please try again')
    ACCOUNT_NOT_FOUND = _('A user with the given credential does not exist.')
    ACCOUNT_ALREADY_EXISTS = _('A user with the given credentials already exists')
    INCORRECT_PASSWORD = _('You have entered an incorrect password, please try again!')
    INVALID_EMAIL = _('You have entered an invalid email address, please try again!')
    INTERNAL_SERVER_ERROR = _('An internal error is encountered!')


class SuccessMessages:
    ACCOUNT_CREATED = _("User Created Successfully!")
    ACCOUNT_LOGIN_SUCCESSFUL = _("User Logged in Successfully!")
    ACCOUNT_LOGOUT_SUCCESSFUL = _("User Logged out Successfully!")
    ACCOUNT_PASSWORD_RESET_SUCCESSFUL = _("User Password Reset Successfully!")
    ACCOUNT_PASSWORD_RESET_EMAIL_SENT = _("User Password Email Successfully!")
