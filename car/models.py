from typing import Any, override

from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.text import slugify

from furai.models import BaseModel

from .enums import CarDrivetrain, CarFeatures, CarFuelType, CarMake, CarTransmission


class CarFeature(BaseModel):
    """Representation of a car feature"""

    name = models.CharField(
        help_text="The name of the car feature",
        db_comment="The name of the car feature",
        max_length=25,
        unique=True,
        choices=CarFeatures,
    )

    def __str__(self) -> str:
        return self.name

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        # Raise an error if the name is not from the CarFeatures enum
        if self.name not in CarFeatures:
            raise ValidationError(
                "A car feature name can only be taken from the available choices"
            )
        super().save(*args, **kwargs)


class Car(BaseModel):
    """Representation of a car available for rent"""

    make = models.CharField(
        help_text="The car brand",
        db_comment="The car brand",
        max_length=50,
        choices=CarMake,
    )
    model = models.CharField(
        help_text="The car model", db_comment="The car model", max_length=50
    )
    slug = models.SlugField(
        help_text="Slugified combination of make and model",
        db_comment="Slugified combination of make and model",
        unique=True,
    )
    capacity = models.IntegerField(
        help_text="The total passenger capacity",
        db_comment="The total passenger capacity",
    )
    transmission = models.CharField(
        help_text="The car transmission",
        db_comment="The car transmission",
        choices=CarTransmission,
    )
    drivetrain = models.CharField(
        help_text="The car drivetrain",
        db_comment="The car drivetrain",
        choices=CarDrivetrain,
    )
    fuel_type = models.CharField(
        help_text="The car fuel type",
        db_comment="The car fuel type",
        choices=CarFuelType,
    )
    fuel_consumption_metric = models.FloatField(
        help_text="The fuel efficiency, represented in liters per 100km (L/100km)",
        db_comment="The fuel efficiency, represented in liters per 100km (L/100km)",
    )
    engine_code = models.CharField(
        help_text="The car engine identifier",
        db_comment="The car engine identifier",
        max_length=12,
    )
    power_hp = models.IntegerField(
        help_text="The engine power in HP",
        db_comment="The engine power in HP",
    )
    power_max_rpm = models.IntegerField(
        help_text="The engine max RPM for the given power",
        db_comment="The engine max RPM for the given power",
    )
    price_hourly_cents = models.IntegerField(
        help_text="The hourly rate of a rental, in cents",
        db_comment="The hourly rate of a rental, in cents",
    )
    price_three_hours_cents = models.IntegerField(
        help_text="The price for a 3 hours rental, in cents",
        db_comment="The price for a 3 hours rental, in cents",
    )
    price_six_hours_cents = models.IntegerField(
        help_text="The price for a 6 hours rental, in cents",
        db_comment="The price for a 6 hours rental, in cents",
    )
    price_nine_hours_cents = models.IntegerField(
        help_text="The price for a 9 hours rental, in cents",
        db_comment="The price for a 9 hours rental, in cents",
    )
    price_twelve_hours_cents = models.IntegerField(
        help_text="The price for a 12 hours rental, in cents",
        db_comment="The price for a 12 hours rental, in cents",
    )
    price_twenty_four_hours_cents = models.IntegerField(
        help_text="The price for a 24 hours rental, in cents",
        db_comment="The price for a 24 hours rental, in cents",
    )
    features = models.ManyToManyField(
        CarFeature,
    )

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return f"{self.make} {self.model}"

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        # Set automatically slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("car-details", kwargs={"car_slug": self.slug})


class CarMedia(BaseModel):
    """Representation of a media (picture, video..) linked to a car"""

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        null=True,
        help_text="The car linked to the media",
        db_comment="The car linked to the media",
    )
    url = models.URLField(
        help_text="The full path of the resource",
        db_comment="The full path of the resource",
    )
    is_thumbnail = models.BooleanField(
        help_text="When set to True, the media is used as the car thumbnail",
        db_comment="When set to True, the media is used as the car thumbnail",
    )

    def __str__(self) -> str:
        return self.url

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        # Ensure only one thumbnail is linked to a car
        thumbnail_count = CarMedia.objects.filter(
            car=self.car, is_thumbnail=True
        ).count()
        if self.is_thumbnail and thumbnail_count > 0:
            raise ValidationError("Cannot assign multiple thumbnails for one car")

        super().save(*args, **kwargs)
