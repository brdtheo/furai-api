from rest_framework.routers import DefaultRouter

from .views import CarFeatureViewSet, CarMediaViewSet, CarViewSet

router = DefaultRouter(trailing_slash=False)
router.register(
    "cars",
    CarViewSet,
    basename="cars",
)
router.register(
    "car-medias",
    CarMediaViewSet,
    basename="car-medias",
)
router.register(
    "car-features",
    CarFeatureViewSet,
    basename="car-features",
)
urlpatterns = router.urls
