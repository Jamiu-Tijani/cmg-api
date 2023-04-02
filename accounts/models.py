from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from cloudinary.models import CloudinaryField
from datetime import datetime,timezone,timedelta
from django.conf import settings



class Timestamp(models.Model):
    """
    Timestamp mixin to inherit
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # prevent dj from creating a column for this table
    class Meta:
        abstract = True


class Account(User, Timestamp):
    GENDER_MALE = "m"
    GENDER_FEMALE = "f"
    OTHER = "o"

    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (OTHER, "Other"),
    )
    username = models.CharField(null=True,blank=True, max_length=255)
    owner_id = models.UUIDField(default=uuid.uuid4, editable=False)
    profile_picture = CloudinaryField('image')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.user.username

    @property
    def last_seen(self):
        return cache.get(f"seen_{self.user.username}")

    @property
    def online(self):
        if self.last_seen:
            now = datetime.now(timezone.utc)
            if now > self.last_seen + timedelta(minutes=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

    def __str__(self):
        return f'{self.username}'



# this model Stores the data of the emails verified
class EmailToken(models.Model):
    email = models.CharField(max_length=80, null=True, blank=True)
    is_verified = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return str(self.email)
