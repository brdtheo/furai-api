from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from user.models import CustomUser


class TestClientAuthenticator:
    """
    A class containing static methods to ease authentication within tests
    """

    @staticmethod
    def authenticate(client: APIClient, user: CustomUser | str) -> None:
        """Authenticate the test client from a CustomUser instance or email"""

        if isinstance(user, CustomUser):
            user_instance = user
        else:
            user_instance = CustomUser.objects.get(email=user)
        token = Token.objects.create(user=user_instance)
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    @staticmethod
    def authenticate_logout(client: APIClient) -> None:
        """Clear test client authentication credentials"""

        client.credentials()
