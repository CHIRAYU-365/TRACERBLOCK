from django.db import models
from users.models import CustomUser

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    manufacturer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='products_manufactured')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} at {self.warehouse.name} ({self.quantity})"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
    )
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders_placed')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders_received')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

class QualityCheck(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inspector = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    passed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class TrackingEvent(models.Model):
    product = models.ForeignKey(Product, related_name='events', on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)

class Telemetry(models.Model):
    event = models.ForeignKey(TrackingEvent, on_delete=models.CASCADE, related_name='telemetry')
    temperature_c = models.FloatField()
    humidity_percent = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
