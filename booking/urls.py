from rest_framework.routers import DefaultRouter

from .views import BookingViewSet

router = DefaultRouter(trailing_slash=False)
router.register(
    "bookings",
    BookingViewSet,
    basename="bookings",
)
urlpatterns = router.urls
