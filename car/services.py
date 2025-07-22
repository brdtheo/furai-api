from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .enums import CarFeatures
from .errors import CAR_FEATURE_INVALID_NAME_ERROR, CAR_MEDIA_MULTIPLE_THUMBNAIL_ERROR
from .models import Car, CarFeature, CarMedia


class CarService:
    """
    Service class for Car instances
    """

    def __init__(
        self,
        make: str,
        model: str,
        capacity: int,
        transmission: str,
        drivetrain: str,
        fuel_type: str,
        fuel_consumption_metric: float,
        engine_code: str,
        power_hp: int,
        power_max_rpm: int,
        price_hourly_cents: int,
        price_three_hours_cents: int,
        price_six_hours_cents: int,
        price_nine_hours_cents: int,
        price_twenty_four_hours_cents: int,
        id: int | None = None,
    ) -> None:
        from .models import Car

        self.model_class = Car
        self.make = make
        self.model = model
        self.capacity = capacity
        self.transmission = transmission
        self.drivetrain = drivetrain
        self.fuel_type = fuel_type
        self.fuel_consumption_metric = fuel_consumption_metric
        self.engine_code = engine_code
        self.power_hp = power_hp
        self.power_max_rpm = power_max_rpm
        self.price_hourly_cents = price_hourly_cents
        self.price_three_hours_cents = price_three_hours_cents
        self.price_six_hours_cents = price_six_hours_cents
        self.price_nine_hours_cents = price_nine_hours_cents
        self.price_twenty_four_hours_cents = price_twenty_four_hours_cents
        self.id = id

    @transaction.atomic
    def create(self) -> Car:
        slug = slugify(f"{self.make} {self.model}")
        car = super(
            self.model_class._default_manager.__class__,
            self.model_class._default_manager,
        ).create(
            slug=slug,
            make=self.make,
            model=self.model,
            capacity=self.capacity,
            transmission=self.transmission,
            drivetrain=self.drivetrain,
            fuel_type=self.fuel_type,
            fuel_consumption_metric=self.fuel_consumption_metric,
            engine_code=self.engine_code,
            power_hp=self.power_hp,
            power_max_rpm=self.power_max_rpm,
            price_hourly_cents=self.price_hourly_cents,
            price_three_hours_cents=self.price_three_hours_cents,
            price_six_hours_cents=self.price_six_hours_cents,
            price_nine_hours_cents=self.price_nine_hours_cents,
            price_twenty_four_hours_cents=self.price_twenty_four_hours_cents,
        )

        return car

    @transaction.atomic
    def update(self) -> Car:
        car = get_object_or_404(self.model_class, pk=self.id)

        if (car.make != self.make) or (car.model != self.model):
            slug = slugify(f"{self.make} {self.model}")
        else:
            slug = car.slug

        (
            super(  # type: ignore
                self.model_class._default_manager.__class__,
                self.model_class._default_manager,
            )
            .filter(id=car.pk)
            .update(
                slug=slug,
                make=self.make,
                model=self.model,
                capacity=self.capacity,
                transmission=self.transmission,
                drivetrain=self.drivetrain,
                fuel_type=self.fuel_type,
                fuel_consumption_metric=self.fuel_consumption_metric,
                engine_code=self.engine_code,
                power_hp=self.power_hp,
                power_max_rpm=self.power_max_rpm,
                price_hourly_cents=self.price_hourly_cents,
                price_three_hours_cents=self.price_three_hours_cents,
                price_six_hours_cents=self.price_six_hours_cents,
                price_nine_hours_cents=self.price_nine_hours_cents,
                price_twenty_four_hours_cents=self.price_twenty_four_hours_cents,
            )
        )

        return car


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
