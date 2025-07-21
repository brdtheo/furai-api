from rest_framework import exceptions, status

CUSTOMER_PASSPORT_NUMBER_REQUIRED_ERROR = exceptions.ValidationError(
    detail={"passport": "Passport number is required for foreign nationals"},
    code=str(status.HTTP_400_BAD_REQUEST),
)
