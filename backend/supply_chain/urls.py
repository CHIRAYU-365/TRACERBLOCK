from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProductViewSet, TrackingEventViewSet, TelemetryViewSet,
                    WarehouseViewSet, InventoryViewSet, PurchaseOrderViewSet, QualityCheckViewSet, UserViewSet,
                    get_stockout_prediction, get_supplier_score, get_carbon_emissions)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'events', TrackingEventViewSet)
router.register(r'telemetry', TelemetryViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'orders', PurchaseOrderViewSet)
router.register(r'quality', QualityCheckViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('insights/stockout/<int:inventory_id>/', get_stockout_prediction),
    path('insights/supplier/<int:supplier_id>/', get_supplier_score),
    path('insights/carbon/<int:product_id>/', get_carbon_emissions),
    path('', include(router.urls)),
]
