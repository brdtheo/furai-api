from typing import TYPE_CHECKING

from django.db import transaction

from .enums import CarFeatures
from .errors import CAR_FEATURE_INVALID_NAME_ERROR

if TYPE_CHECKING:
    from .models import CarFeature


class CarFeatureService:
    """
    Service class for CarFeature instances
    """

    def __init__(self, name: str) -> None:
        from .models import CarFeature

        self.model_class = CarFeature
        self.name = name

    @transaction.atomic
    def create(self) -> "CarFeature":
        if self.name not in CarFeatures:
            raise CAR_FEATURE_INVALID_NAME_ERROR

        car_feature = super(
            self.model_class._default_manager.__class__,
            self.model_class._default_manager,
        ).create(name=self.name)

        return car_feature
