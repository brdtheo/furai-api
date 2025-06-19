from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase

from .enums import CarDrivetrain, CarFeatures, CarFuelType, CarMake, CarTransmission
from .models import Car, CarFeature, CarMedia


def set_up_car() -> Car:
    """Creates a Car instances in the test DB"""
    car = Car.objects.create(
        make=CarMake.SUBARU,
        model="WRX STI",
        capacity=4,
        transmission=CarTransmission.MANUAL,
        drivetrain=CarDrivetrain.FOUR_WHEEL_DRIVE,
        fuel_type=CarFuelType.GASOHOL_95,
        fuel_consumption_metric=8.7,
        engine_code="EJ207",
        power_hp=280,
        power_max_rpm=7000,
        price_hourly_cents=50000,
        price_9_hours_cents=300000,
        price_12_hours_cents=350000,
        price_24_hours_cents=450000,
    )
    return car


def set_up_car_features():
    """Creates a list of CarFeature instances in the test DB"""
    for feature in CarFeatures:
        CarFeature.objects.create(name=feature)


def set_up_car_media_list(car: Car):
    """Creates a list of CarMedia instances in the test DB"""
    for i in range(10):
        CarMedia.objects.create(
            car=car, url="https://picsum.photos/250/250", is_thumbnail=bool(i == 0)
        )


class CarTestCase(TestCase):
    def setUp(self):
        car = set_up_car()
        set_up_car_features()
        self.car = car

    def test_create_car(self):
        """Correctly creates a car"""
        assert self.car.make == CarMake.SUBARU
        assert self.car.model == "WRX STI"
        assert self.car.capacity == 4
        assert self.car.transmission == CarTransmission.MANUAL
        assert self.car.drivetrain == CarDrivetrain.FOUR_WHEEL_DRIVE
        assert self.car.fuel_type == CarFuelType.GASOHOL_95
        assert self.car.fuel_consumption_metric == 8.7
        assert self.car.engine_code == "EJ207"
        assert self.car.power_hp == 280
        assert self.car.power_max_rpm == 7000
        assert self.car.price_hourly_cents == 50000
        assert self.car.price_9_hours_cents == 300000
        assert self.car.price_12_hours_cents == 350000
        assert self.car.price_24_hours_cents == 450000

    def test_name(self):
        assert self.car.name == f"{self.car.make} {self.car.model}"

    def test_update_car(self):
        """Correctly updates a car"""
        self.car.power_hp = 320
        self.car.power_max_rpm = 6800
        self.car.price_hourly_cents = 45000
        self.car.save()
        assert self.car.power_hp == 320
        assert self.car.power_max_rpm == 6800
        assert self.car.price_hourly_cents == 45000

    def test_add_linked_feature(self):
        """Correctly link a car feature to a car"""
        car_feature = CarFeature.objects.get(pk=1)
        self.car.features.add(car_feature)
        linked_feature = self.car.features.get(pk=1)
        assert linked_feature is not None
        assert linked_feature.name == car_feature.name

    def test_clear_linked_features(self):
        """Correctly clears all car features linked to a car"""
        car_feature__list = CarFeature.objects.all()[:5]
        self.car.features.set(car_feature__list)
        assert self.car.features.count() == 5
        self.car.features.clear()
        assert self.car.features.count() == 0

    def test_delete_car(self):
        """Correctly deletes a car"""
        assert Car.objects.count() == 1
        self.car.delete()
        assert Car.objects.count() == 0


class CarMediaTestCase(TestCase):
    def setUp(self):
        car = set_up_car()
        set_up_car_features()
        set_up_car_media_list(car)
        self.car = car

    def test_create_car_media(self):
        """Correctly creates car medias"""
        assert CarMedia.objects.count() == 10

    def test_update_car_media_url(self):
        """Correctly updates a car media url"""
        media = CarMedia.objects.last()
        if media is not None:
            media.url = "https://picsum.photos/250/250"
            media.save()
            assert media.url == "https://picsum.photos/250/250"
        pass

    def test_delete_car_media(self):
        """Correctly deletes a car media"""
        media = CarMedia.objects.last()
        if media is not None:
            media.delete()
            assert CarMedia.objects.count() == 9
        pass

    def test_cascade_delete_car_media(self):
        """All car medias should be deleted when a car is deleted"""
        self.car.delete()
        assert CarMedia.objects.count() == 0

    def test_create_multiple_car_thumbnails(self):
        """A car should only have one thumbnail"""
        with self.assertRaises(ValidationError):
            CarMedia.objects.create(
                car=self.car,
                url="https://picsum.photos/250/250",
                is_thumbnail=True,
            )

    def test_update_is_thumbnail(self):
        """We should be able to update which instance is the thumbnail"""
        thumbnail = CarMedia.objects.get(is_thumbnail=True)
        new_thumbnail = CarMedia.objects.filter(is_thumbnail=False)[0]
        thumbnail.is_thumbnail = False
        new_thumbnail.is_thumbnail = True
        thumbnail.save()
        new_thumbnail.save()
        assert thumbnail.is_thumbnail is False
        assert new_thumbnail.is_thumbnail is True


class CarFeatureTestCase(TestCase):
    def setUp(self):
        car = set_up_car()
        set_up_car_features()
        self.car = car

    def test_create_car_feature(self):
        """Correctly creates a car feature"""
        assert CarFeature.objects.count() == len(CarFeatures)

    def test_fail_create_car_feature(self):
        """Fails to create a car feature if the name is not from CarFeatures enum"""
        with self.assertRaises(ValidationError):
            CarFeature.objects.create(name="foo")

    def test_fail_update_car_feature(self):
        """Fails to update a car feature if another object with the same name already exists"""
        car_feature = CarFeature.objects.first()
        if car_feature is not None:
            car_feature.name = CarFeatures.USB_PORTS
            with self.assertRaises(IntegrityError):
                car_feature.save()
        pass

    def test_delete_car_feature(self):
        """Correctly deletes a car feature"""
        count = CarFeature.objects.count()
        car_feature = CarFeature.objects.first()
        if car_feature is not None:
            car_feature.delete()
            assert CarFeature.objects.count() == count - 1
        pass
