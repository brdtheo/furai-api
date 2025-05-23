from django.forms import ValidationError
from django.test import TestCase

from .models import CustomUser


class CustomUserTestCase(TestCase):
    def test_create_user(self):
        """Correctly creates a regular user"""
        CustomUser.objects.create(email="a@a.fr")
        user = CustomUser.objects.get(email="a@a.fr")
        assert user is not None
        assert user.email is not None
        assert not user.password
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_fail_create_user_missing_email(self):
        """Fails to create a regular user if email is not provided"""
        with self.assertRaises(TypeError):
            CustomUser.objects.create_user()

    def test_fail_create_user_with_password(self):
        """Fails to create a regular user if a password is provided"""
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(email="a@a.fr", password="foo")

    def test_create_superuser(self):
        """Correctly creates a super user"""
        CustomUser.objects.create_superuser(email="a@a.fr", password="foo")
        user = CustomUser.objects.get(email="a@a.fr")
        assert user is not None
        assert user.email is not None
        assert user.password is not None
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True
