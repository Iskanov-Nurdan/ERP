from rest_framework.routers import DefaultRouter
from .views import ProductionLineViewSet

router = DefaultRouter()
router.register("lines", ProductionLineViewSet, basename="production-line")

urlpatterns = router.urls
