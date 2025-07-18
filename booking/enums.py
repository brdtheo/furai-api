from django.db.models import TextChoices


class BookingStatus(TextChoices):
    COMPLETED = "COMPLETED"
    ACTIVE = "ACTIVE"
    UNPAID = "UNPAID"
    CANCELED_BY_STAFF = "CANCELED_BY_STAFF"
    CANCELED_BY_CUSTOMER = "CANCELED_BY_CUSTOMER"
