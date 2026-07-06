import os
import sys
import django
from datetime import timedelta
import random

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from users.models import CustomUser
from supply_chain.models import Product, Warehouse, Inventory, PurchaseOrder, QualityCheck, TrackingEvent, Telemetry

def generate():
    print("Generating AI Mock Data...")
    
    admin, _ = CustomUser.objects.get_or_create(username="admin", role="ADMIN")
    admin.set_password("admin")
    admin.save()
    
    mfg, _ = CustomUser.objects.get_or_create(username="global_pharma", role="MANUFACTURER")
    mfg.set_password("password")
    mfg.save()
    
    dist, _ = CustomUser.objects.get_or_create(username="fast_logistics", role="DISTRIBUTOR")
    dist.set_password("password")
    dist.save()
    
    wh, _ = Warehouse.objects.get_or_create(name="Central Hub", location="New York", manager=dist)
    
    product, _ = Product.objects.get_or_create(name="Vaccine Batch X", description="Temperature sensitive", manufacturer=mfg)
    
    inv, _ = Inventory.objects.get_or_create(product=product, warehouse=wh)
    inv.quantity = 500
    inv.save()

    # Generate historical POs to simulate demand (linear decrease in stock)
    base_time = timezone.now() - timedelta(days=30)
    for i in range(10):
        po, created = PurchaseOrder.objects.get_or_create(
            buyer=dist,
            seller=mfg,
            product=product,
            quantity=50,
            status='DELIVERED',
        )
        # Hack created_at because auto_now_add ignores passed value
        po.created_at = base_time + timedelta(days=i*3)
        po.save()

    # Generate QC history (80% pass rate)
    for i in range(10):
        QualityCheck.objects.create(
            product=product,
            inspector=admin,
            passed=(i % 5 != 0)  # 2 fails out of 10
        )

    # Generate Tracking and Telemetry for Carbon Emissions
    for i in range(15):
        event = TrackingEvent.objects.create(
            product=product,
            status="In Transit",
            location=f"Checkpoint {i}"
        )
        Telemetry.objects.create(
            event=event,
            temperature_c=random.uniform(2.0, 8.0),
            humidity_percent=random.uniform(40, 60)
        )

    print("Data generation complete!")

if __name__ == "__main__":
    generate()
