from django.db import transaction

from .enums import CarFeatures
from .errors import CAR_FEATURE_INVALID_NAME_ERROR, CAR_MEDIA_MULTIPLE_THUMBNAIL_ERROR
from .models import CarFeature, CarMedia


class CarFeatureService:
    """
    Service class for CarFeature instances
    """

    def __init__(self, name: str) -> None:
        from .models import CarFeature

        self.model_class = CarFeature
        self.name = name

    @transaction.atomic
    def create(self) -> CarFeature:
        if self.name not in CarFeatures:
            raise CAR_FEATURE_INVALID_NAME_ERROR

        car_feature = super(
            self.model_class._default_manager.__class__,
            self.model_class._default_manager,
        ).create(name=self.name)

        return car_feature


class CarMediaService:
    """
    Service class for CarMedia instances
    """

    def __init__(self, car: int, url: str, is_thumbnail: bool = False) -> None:
        from .models import CarMedia

        self.model_class = CarMedia
        self.car = car
        self.url = url
        self.is_thumbnail = is_thumbnail

    @transaction.atomic
    def create(self) -> CarMedia:
        car_thumbnail_exists = CarMedia.objects.filter(
            car=self.car, is_thumbnail=True
        ).exists()
        if self.is_thumbnail and car_thumbnail_exists:
            raise CAR_MEDIA_MULTIPLE_THUMBNAIL_ERROR

        car_media = super(
            self.model_class._default_manager.__class__,
            self.model_class._default_manager,
        ).create(car=self.car, url=self.url, is_thumbnail=self.is_thumbnail)

        return car_media
