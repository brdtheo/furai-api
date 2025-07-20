from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APITestCase

from .enums import CarDrivetrain, CarFeatures, CarFuelType, CarMake, CarTransmission
from .models import Car, CarFeature, CarMedia

fake = Faker()


def set_up_car() -> Car:
    """Creates a Car instances in the test DB"""

    car = Car.objects.create(
        make=fake.enum(CarMake),
        model=" ".join(fake.words(2)),
        capacity=fake.random_element([2, 4, 5]),
        transmission=fake.enum(CarTransmission),
        drivetrain=fake.enum(CarDrivetrain),
        fuel_type=fake.enum(CarFuelType),
        fuel_consumption_metric=fake.pyfloat(
            min_value=5.0, max_value=12.0, positive=True, right_digits=2
        ),
        engine_code=fake.pystr(min_chars=5, max_chars=8).upper(),
        power_hp=fake.pyint(150, 400),
        power_max_rpm=fake.pyint(6500, 9000, 500),
        price_hourly_cents=fake.pyint(800, 1000, 500),
        price_three_hours_cents=fake.pyint(2000, 2500, 500),
        price_six_hours_cents=fake.pyint(3800, 4200, 500),
        price_nine_hours_cents=fake.pyint(4800, 5500, 500),
        price_twelve_hours_cents=fake.pyint(6000, 7000, 5000),
        price_twenty_four_hours_cents=fake.pyint(7200, 8500, 5000),
    )
    return car


def set_up_car_features():
    """Creates a list of CarFeature instances in the test DB"""
    for feature in CarFeatures:
        CarFeature.objects.create(name=feature)
    return CarFeature.objects.all()


def set_up_car_media_list(car: Car):
    """Creates a list of CarMedia instances in the test DB"""
    for i in range(10):
        CarMedia.objects.create(
            car=car, url=fake.image_url(), is_thumbnail=bool(i == 0)
        )


class CarTestCase(TestCase):
    def setUp(self):
        car = set_up_car()
        set_up_car_features()
        self.car = car

    def test_name(self):
        """Returns the car name from the make and the model"""

        assert self.car.name == f"{self.car.make} {self.car.model}"

    def test_update_car(self):
        """Correctly updates a car"""

        new_power_hp = fake.pyint(150, 400, 20)
        new_power_max_rpm = fake.pyint(6500, 9000, 500)
        new_price_hourly_cents = fake.pyint(30000, 80000, 500)
        self.car.power_hp = new_power_hp
        self.car.power_max_rpm = new_power_max_rpm
        self.car.price_hourly_cents = new_price_hourly_cents
        self.car.save()
        assert self.car.power_hp == new_power_hp
        assert self.car.power_max_rpm == new_power_max_rpm
        assert self.car.price_hourly_cents == new_price_hourly_cents

    def test_add_linked_feature(self):
        """Correctly link a car feature to a car"""

        car_feature = CarFeature.objects.first()
        self.car.features.add(car_feature)
        linked_feature = self.car.features.first()
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

    def test_representation_string(self):
        """Returns the instance representation correctly"""

        assert self.car.__str__() == self.car.name


class CarAPITestCase(APITestCase):
    def setUp(self):
        car = set_up_car()
        set_up_car_features()
        self.car = car

    def test_get_car_list(self):
        """Correctly list all cars"""

        url = reverse("cars-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK

    def test_get_car_detail(self):
        """Correctly retrieves a car instance"""

        url = reverse("cars-detail", kwargs={"pk": self.car.pk})
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK

    def test_get_car_detail_not_found(self):
        """Returns a 404 HTTP status for cars that dont exist"""

        url = reverse("cars-detail", kwargs={"pk": 999999})
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_404_NOT_FOUND


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
            new_url = fake.image_url()
            media.url = new_url
            media.save()
            assert media.url == new_url
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
                url=fake.image_url(),
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

    def test_representation_string(self):
        """Returns the instance representation correctly"""

        car_media = CarMedia.objects.first()
        assert car_media.__str__() == car_media.url


class CarMediaAPITestCase(APITestCase):
    def setUp(self):
        car = set_up_car()
        set_up_car_features()
        set_up_car_media_list(car)
        self.car = car

    def test_get_car_media_list(self):
        """Correctly list all car medias"""

        url = reverse("car-medias-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK

    def test_get_car_media_list_car_linked(self):
        """Correctly list all car medias related to a car instance"""

        url = reverse("car-medias-list", query={"car": self.car.pk})
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK

    def test_get_car_media_list_is_thumbnail(self):
        """Correctly list all car medias according to the is_thumbnail search param"""

        is_thumbnail_url = reverse("car-medias-list", query={"is_thumbnail": "true"})
        is_not_thumbnail_url = reverse(
            "car-medias-list", query={"is_thumbnail": "false"}
        )
        thumbnail_list_response = self.client.get(is_thumbnail_url, format="json")
        no_thumbnail_list_response = self.client.get(
            is_not_thumbnail_url, format="json"
        )
        assert thumbnail_list_response.status_code == HTTP_200_OK
        assert no_thumbnail_list_response.status_code == HTTP_200_OK
        for car_media in thumbnail_list_response.data["results"]:
            assert car_media["is_thumbnail"] is True
        for car_media in no_thumbnail_list_response.data["results"]:
            assert car_media["is_thumbnail"] is False


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

    def test_representation_string(self):
        """Returns the instance representation correctly"""

        car_feature = CarFeature.objects.first()
        assert car_feature.__str__() == car_feature.name


class CarFeatureAPITestCase(APITestCase):
    def setUp(self):
        car = set_up_car()
        car_feature_list = set_up_car_features()
        self.car = car
        self.car_feature_list = car_feature_list

    def test_get_car_feature_list(self):
        """Correctly list all car features"""

        url = reverse("car-features-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK
        assert response.data["count"] == len(CarFeatures)

    def test_get_car_feature_list_id__in(self):
        """Correctly list all car features from a list of id"""

        id_list = [car_feature.id for car_feature in self.car_feature_list[:3]]
        url = reverse("car-features-list")
        response = self.client.get(
            url, data={"id__in": ",".join(map(str, id_list))}, format="json"
        )
        assert response.status_code == HTTP_200_OK
        assert response.data["count"] == len(id_list)
        for car_feature in response.data["results"]:
            assert car_feature["id"] in id_list
