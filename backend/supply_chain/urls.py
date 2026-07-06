from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProductViewSet, TrackingEventViewSet, TelemetryViewSet,
                    WarehouseViewSet, InventoryViewSet, PurchaseOrderViewSet, QualityCheckViewSet)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'events', TrackingEventViewSet)
router.register(r'telemetry', TelemetryViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'orders', PurchaseOrderViewSet)
router.register(r'quality', QualityCheckViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
