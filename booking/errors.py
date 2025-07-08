from rest_framework import exceptions, status

BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR = exceptions.ValidationError(
    detail="This car is not available during this time period",
    code=str(status.HTTP_400_BAD_REQUEST),
)

BOOKING_START_DATE_IN_THE_PAST_ERROR = exceptions.ValidationError(
    detail="The start date of a booking cannot be in the past",
    code=str(status.HTTP_400_BAD_REQUEST),
)


BOOKING_END_DATE_IN_THE_PAST_ERROR = exceptions.ValidationError(
    detail="The end date of a booking cannot be in the past",
    code=str(status.HTTP_400_BAD_REQUEST),
)

BOOKING_END_DATE_BEFORE_START_DATE_ERROR = exceptions.ValidationError(
    detail="The end date of a booking cannot be before the start date",
    code=str(status.HTTP_400_BAD_REQUEST),
)

BOOKING_SAME_DAY_BOOKING_ERROR = exceptions.ValidationError(
    detail="A booking cannot created on the same day",
    code=str(status.HTTP_400_BAD_REQUEST),
)

BOOKING_CUSTOMER_PASSPORT_REQUIRED_ERROR = exceptions.ValidationError(
    detail="A passport number is required for foreign national",
    code=str(status.HTTP_400_BAD_REQUEST),
)
