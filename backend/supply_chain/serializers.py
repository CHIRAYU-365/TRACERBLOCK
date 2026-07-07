from rest_framework import serializers
from .models import Product, TrackingEvent, Telemetry, Warehouse, Inventory, PurchaseOrder, QualityCheck

class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = '__all__'

class TrackingEventSerializer(serializers.ModelSerializer):
    telemetry = TelemetrySerializer(many=True, read_only=True)
    class Meta:
        model = TrackingEvent
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    events = TrackingEventSerializer(many=True, read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.username', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class QualityCheckSerializer(serializers.ModelSerializer):
    inspector_name = serializers.CharField(source='inspector.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = QualityCheck
        fields = '__all__'

from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role', 'organization', 'first_name', 'last_name']
