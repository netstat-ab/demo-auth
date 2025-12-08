__all__ = [
    'User',
    'Registration',
]

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    email = models.EmailField(unique=True)
    has_verified_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Registration(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    code = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
