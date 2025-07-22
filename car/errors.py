from rest_framework import exceptions, status

from .enums import CarFeatures

CAR_FEATURE_INVALID_NAME_ERROR = exceptions.ValidationError(
    detail={
        "name": f"Invalid car feature name. Available options are: {[car_feature.name for car_feature in CarFeatures]}"
    },
    code=str(status.HTTP_400_BAD_REQUEST),
)
