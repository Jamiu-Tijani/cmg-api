import random
import string
from datetime import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.conf import settings as django_settings


class GenerateKey:
    @staticmethod
    def return_value(email):
        return str(email) + str(datetime.date(datetime.now())) + django_settings.SECRET_KEY



def generate_token():
    token = "".join(random.choice(string.digits) for x in range(4))
    return token



def validate_email_(email):
    try:
        validate_email(email.strip())
        return True
    except ValidationError:
        return False
