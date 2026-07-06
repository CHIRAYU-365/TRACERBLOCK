from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product, TrackingEvent, Telemetry, Warehouse, Inventory, PurchaseOrder, QualityCheck
from .serializers import (ProductSerializer, TrackingEventSerializer, TelemetrySerializer, 
                          WarehouseSerializer, InventorySerializer, PurchaseOrderSerializer, QualityCheckSerializer)
from blockchain.service import log_event_to_blockchain

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(manufacturer=self.request.user)
        else:
            serializer.save()

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class QualityCheckViewSet(viewsets.ModelViewSet):
    queryset = QualityCheck.objects.all()
    serializer_class = QualityCheckSerializer

class TelemetryViewSet(viewsets.ModelViewSet):
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer

class TrackingEventViewSet(viewsets.ModelViewSet):
    queryset = TrackingEvent.objects.all()
    serializer_class = TrackingEventSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        
        # Log to blockchain
        try:
            tx_hash = log_event_to_blockchain(
                product_id=event.product.id,
                status=event.status,
                location=event.location
            )
            event.tx_hash = tx_hash
            event.save()
        except Exception as e:
            print(f"Blockchain logging failed: {e}")
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
