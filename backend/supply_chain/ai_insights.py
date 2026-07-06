from datetime import timedelta
from django.utils import timezone
from .models import PurchaseOrder, QualityCheck, TrackingEvent, Inventory
from sklearn.linear_model import LinearRegression
import numpy as np

def predict_stockout(inventory_id):
    """Predicts how many days until an inventory item runs out based on historical sales."""
    try:
        inv = Inventory.objects.get(id=inventory_id)
    except Inventory.DoesNotExist:
        return {"error": "Inventory not found"}

    recent_orders = PurchaseOrder.objects.filter(
        product=inv.product, 
        status='DELIVERED', 
        created_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('created_at')

    if not recent_orders.exists():
        return {"days_until_stockout": "Insufficient Data", "current_stock": inv.quantity}

    X = np.array([(order.created_at - timezone.now() + timedelta(days=30)).days for order in recent_orders]).reshape(-1, 1)
    y = np.cumsum([order.quantity for order in recent_orders])

    if len(X) < 2:
        return {"days_until_stockout": "Insufficient Data", "current_stock": inv.quantity}

    model = LinearRegression().fit(X, y)
    daily_demand_rate = model.coef_[0]

    if daily_demand_rate <= 0:
        return {"days_until_stockout": "Infinite", "current_stock": inv.quantity}

    days_left = inv.quantity / daily_demand_rate
    return {
        "days_until_stockout": max(0, int(days_left)),
        "current_stock": inv.quantity,
        "daily_demand_rate": round(daily_demand_rate, 2)
    }

def calculate_supplier_score(supplier_user_id):
    """Calculates a Trust Score (0-100) based on QA pass rates and delivery speed."""
    orders = PurchaseOrder.objects.filter(seller_id=supplier_user_id)
    qc_checks = QualityCheck.objects.filter(product__manufacturer_id=supplier_user_id)
    
    if not orders.exists() and not qc_checks.exists():
        return {"score": "N/A", "reason": "No data available"}

    qc_score = 100
    if qc_checks.exists():
        passed_qc = qc_checks.filter(passed=True).count()
        qc_score = (passed_qc / qc_checks.count()) * 100

    delivered_orders = orders.filter(status='DELIVERED').count()
    total_orders = orders.count()
    
    delivery_score = 100
    if total_orders > 0:
        delivery_score = (delivered_orders / total_orders) * 100

    total_score = (qc_score * 0.6) + (delivery_score * 0.4)
    
    return {
        "score": round(total_score, 1),
        "qc_pass_rate": f"{round(qc_score, 1)}%",
        "fulfillment_rate": f"{round(delivery_score, 1)}%"
    }

def estimate_carbon_emissions(product_id):
    """Estimates CO2 emissions based on the number of tracking events (simulating distance)."""
    events_count = TrackingEvent.objects.filter(product_id=product_id).count()
    
    estimated_distance_km = events_count * 500
    emissions_kg = (estimated_distance_km * 100) / 1000

    return {
        "estimated_distance_km": estimated_distance_km,
        "estimated_co2_kg": emissions_kg
    }
