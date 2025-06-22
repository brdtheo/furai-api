from django.forms import ValidationError
from django.test import TestCase
from faker import Faker

from .models import CustomUser

fake = Faker()


class CustomUserTestCase(TestCase):
    def test_create_user(self):
        """Correctly creates a regular user"""

        user_email = fake.email()
        CustomUser.objects.create(email=user_email)
        user = CustomUser.objects.get(email=user_email)
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
            CustomUser.objects.create_user(email=fake.email(), password=fake.password())

    def test_create_superuser(self):
        """Correctly creates a super user"""

        user_email = fake.email()
        CustomUser.objects.create_superuser(email=user_email, password=fake.password())
        user = CustomUser.objects.get(email=user_email)
        assert user is not None
        assert user.email is not None
        assert user.password is not None
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True
