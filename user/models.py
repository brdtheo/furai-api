from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError

from furai.models import BaseModel


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email: str,
        password: str | None = None,
        is_staff: bool = False,
        is_superuser: bool = False,
        **kwargs: Any,
    ):
        if not email:
            raise ValidationError("Email is a required field")

        user: CustomUser = self.model(email=self.normalize_email(email))

        if password and not (is_superuser or is_staff):
            raise ValidationError("Password is not allowed for regular users")

        if password and (is_superuser or is_staff):
            user.set_password(password)
        else:
            user.set_unusable_password()

        if is_staff:
            user.is_staff = True
        if is_superuser:
            user.is_superuser = True

        user.save()
        return user

    def create_superuser(self, email: str, password: str | None = None, **kwargs: Any):
        user = self.create_user(
            email=email, password=password, is_staff=True, is_superuser=True
        )
        user.save()
        return user


class CustomUser(AbstractUser, BaseModel):
    """Representation of a User - solely for auth purposes"""

    username = None
    first_name = None
    last_name = None
    email = models.EmailField(
        help_text="The user email", db_comment="The user email", unique=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email
