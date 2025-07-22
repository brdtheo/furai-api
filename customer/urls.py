from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet

router = DefaultRouter(trailing_slash=False)
router.register(
    "customers",
    CustomerViewSet,
    basename="customers",
)
urlpatterns = router.urls
