from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product, TrackingEvent, Telemetry, Warehouse, Inventory, PurchaseOrder, QualityCheck
from .serializers import (ProductSerializer, TrackingEventSerializer, TelemetrySerializer, 
                          WarehouseSerializer, InventorySerializer, PurchaseOrderSerializer, QualityCheckSerializer, UserSerializer)
from blockchain.service import log_event_to_blockchain
from users.models import CustomUser

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(manufacturer=self.request.user)
        else:
            serializer.save()

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

class QualityCheckViewSet(viewsets.ModelViewSet):
    queryset = QualityCheck.objects.all()
    serializer_class = QualityCheckSerializer
    permission_classes = [IsAuthenticated]

class TelemetryViewSet(viewsets.ModelViewSet):
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer
    permission_classes = [IsAuthenticated]

class TrackingEventViewSet(viewsets.ModelViewSet):
    queryset = TrackingEvent.objects.all()
    serializer_class = TrackingEventSerializer
    permission_classes = [IsAuthenticated]
    
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
from rest_framework.decorators import api_view, permission_classes
from .ai_insights import predict_stockout, calculate_supplier_score, estimate_carbon_emissions

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stockout_prediction(request, inventory_id):
    try:
        data = predict_stockout(inventory_id)
        return Response(data)
    except Exception as e:
        import sys
        print(f"[Error] Stockout prediction calculation failed: {e}", file=sys.stderr)
        return Response({"error": "An error occurred during demand forecasting analysis."}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_supplier_score(request, supplier_id):
    try:
        data = calculate_supplier_score(supplier_id)
        return Response(data)
    except Exception as e:
        import sys
        print(f"[Error] Supplier rating calculation failed: {e}", file=sys.stderr)
        return Response({"error": "An error occurred during supplier trust calculation."}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_carbon_emissions(request, product_id):
    try:
        data = estimate_carbon_emissions(product_id)
        return Response(data)
    except Exception as e:
        import sys
        print(f"[Error] Carbon offset estimation failed: {e}", file=sys.stderr)
        return Response({"error": "An error occurred during Scope 3 carbon offset analysis."}, status=400)
