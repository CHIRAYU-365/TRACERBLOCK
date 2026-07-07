import streamlit as st
import requests
try:
    from frontend.ui_components import load_custom_css
except ModuleNotFoundError:
    from ui_components import load_custom_css
load_custom_css()

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000/api/")

if "token" not in st.session_state or not st.session_state.token:
    st.warning("Please login from the main page first.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("AI & Analytics Command Center 🧠")
st.markdown("Leveraging Machine Learning to solve real-world SCM problems.")

col1, col2 = st.columns(2)

with col1:
    st.header("Demand Forecasting (AI)")
    st.markdown("Predicts exactly when a warehouse will run out of stock based on historical sales velocity using Linear Regression.")
    
    inv_res = requests.get(f"{API_URL}supply_chain/inventory/", headers=headers)
    if inv_res.status_code == 200:
        inventory_items = {f"{i['product_name']} at {i['warehouse_name']}": i['id'] for i in inv_res.json()}
        if inventory_items:
            selected_inv = st.selectbox("Select Inventory Item to Forecast", list(inventory_items.keys()))
            inv_id = inventory_items[selected_inv]
            
            if st.button("Run AI Forecast"):
                res = requests.get(f"{API_URL}supply_chain/insights/stockout/{inv_id}/", headers=headers)
                data = res.json()
                if "days_until_stockout" in data:
                    st.metric("Predicted Days Until Stockout", data["days_until_stockout"])
                    st.write(f"**Current Stock:** {data['current_stock']} units")
                    st.write(f"**Calculated Daily Demand:** {data.get('daily_demand_rate', 'N/A')} units/day")
                else:
                    st.error(data.get("error", "Failed to run model."))
        else:
            st.info("No inventory data found. Run the mock data script!")

with col2:
    st.header("Supplier Risk Score")
    st.markdown("Automatically scores vendors (0-100) based on their Quality Control pass rates and order fulfillment speeds.")
    
    supplier_id = st.number_input("Enter Supplier/Manufacturer ID (e.g. 2 for mock data)", min_value=1, step=1, value=2)
    if st.button("Calculate Trust Score"):
        res = requests.get(f"{API_URL}supply_chain/insights/supplier/{supplier_id}/", headers=headers)
        data = res.json()
        if "score" in data:
            score = data["score"]
            st.metric("Supplier Trust Score", f"{score}/100")
            st.write(f"**QA Pass Rate:** {data['qc_pass_rate']}")
            st.write(f"**Order Fulfillment Rate:** {data['fulfillment_rate']}")
            
            if score == "N/A":
                st.warning("Not enough data to score.")
            elif float(score) < 50:
                st.error("High Risk Supplier")
            elif float(score) < 80:
                st.warning("Medium Risk Supplier")
            else:
                st.success("Highly Reliable Supplier")

st.markdown("---")
st.header("Scope 3 Carbon Tracking 🌱")
st.markdown("Estimates the CO2 footprint of a product's supply chain journey based on shipping telemetry.")

prod_id = st.number_input("Enter Product ID for Carbon Footprint", min_value=1, step=1)
if st.button("Calculate Footprint"):
    res = requests.get(f"{API_URL}supply_chain/insights/carbon/{prod_id}/", headers=headers)
    data = res.json()
    if "estimated_co2_kg" in data:
        colA, colB = st.columns(2)
        colA.metric("Estimated Journey Distance", f"{data['estimated_distance_km']} km")
        colB.metric("Estimated Carbon Emissions", f"{data['estimated_co2_kg']} kg CO2")
    else:
        st.error("Failed to calculate carbon emissions.")
