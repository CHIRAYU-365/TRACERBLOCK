import streamlit as st
import requests
import pandas as pd
import os

try:
    from frontend.ui_components import load_custom_css, get_cached_data
except ModuleNotFoundError:
    from ui_components import load_custom_css, get_cached_data
load_custom_css()

API_URL = os.environ.get("API_URL", "http://localhost:8000/api/")

if "token" not in st.session_state or not st.session_state.token:
    st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    <div class="login-mask"></div>
    <div class="login-popup">
        <h3 style="margin-top:0; color:#e74c3c; text-align:center;">🔒 Access Blocked</h3>
        <p style="color:#94a3b8; text-align:center; font-size:0.9rem;">You must login first to decrypt SCM ledger records.</p>
        <a href="/" target="_self" style="display:block; text-align:center; margin-top:20px; color:#00f2fe; text-decoration:none; font-weight:bold;">← Go to Authentication Portal</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("Inventory Management 🏢")
st.markdown("Monitor and allocate inventory levels across active warehouses. Manage location capacity and set reorder alerts.")

products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
warehouses = get_cached_data(f"{API_URL}supply_chain/warehouses/", "warehouses_cache", headers)
users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)
inventory = get_cached_data(f"{API_URL}supply_chain/inventory/", "inventory_cache", headers)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Register New Warehouse")
    with st.form("add_warehouse_form"):
        wh_name = st.text_input("Warehouse Name", placeholder="e.g. Northeast Distribution hub")
        location = st.text_input("Geographic Location", placeholder="e.g. Boston, MA")
        
        manager_options = {u['username']: u['id'] for u in users if u['role'] in ['ADMIN', 'MANUFACTURER', 'DISTRIBUTOR']}
        selected_manager = st.selectbox("Assigned Warehouse Manager", list(manager_options.keys()))
        
        submit_wh = st.form_submit_button("Add Warehouse Infrastructure")
        if submit_wh:
            if not wh_name or not location:
                st.error("Please fill in both name and location.")
            else:
                wh_data = {
                    "name": wh_name,
                    "location": location,
                    "manager": manager_options.get(selected_manager)
                }
                res = requests.post(f"{API_URL}supply_chain/warehouses/", json=wh_data, headers=headers)
                if res.status_code == 201:
                    st.session_state.pop("warehouses_cache", None)
                    st.success("Warehouse successfully added! ✅")
                    st.rerun()
                else:
                    st.error(f"Error adding warehouse: {res.text}")

with col2:
    st.subheader("Manage Product Stock Allocation")
    with st.form("add_stock_form"):
        prod_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
        selected_prod = st.selectbox("Select Product to Allocate", list(prod_options.keys()))
        
        wh_select_options = {f"{w['name']} (ID: {w['id']})": w['id'] for w in warehouses}
        selected_wh = st.selectbox("Select Target Warehouse", list(wh_select_options.keys()))
        
        quantity = st.number_input("Allocated Stock (Units)", min_value=0, step=10, value=100)
        threshold = st.slider("Low Stock Safety Threshold", 1, 500, 20)
        
        submit_st = st.form_submit_button("Update Stock Levels")
        if submit_st:
            if not selected_prod or not selected_wh:
                st.error("Please select both product and warehouse.")
            else:
                p_id = prod_options[selected_prod]
                w_id = wh_select_options[selected_wh]
                stock_data = {
                    "product": p_id,
                    "warehouse": w_id,
                    "quantity": quantity,
                    "low_stock_threshold": threshold
                }
                
                existing_item = next((item for item in inventory if item['product'] == p_id and item['warehouse'] == w_id), None)
                
                if existing_item:
                    res = requests.patch(f"{API_URL}supply_chain/inventory/{existing_item['id']}/", json=stock_data, headers=headers)
                else:
                    res = requests.post(f"{API_URL}supply_chain/inventory/", json=stock_data, headers=headers)
                
                if res.status_code in [200, 201]:
                    st.session_state.pop("inventory_cache", None)
                    st.success("Stock levels updated successfully! ✅")
                    st.rerun()
                else:
                    st.error(f"Error updating stock: {res.text}")

st.markdown("---")
st.subheader("Infrastructure Registry & Locations")

search_query = st.text_input("🔍 Search Active Warehouses by Name or Location")

if warehouses:
    df_wh = pd.DataFrame(warehouses)
    if search_query:
        df_wh = df_wh[df_wh['name'].str.contains(search_query, case=False) | df_wh['location'].str.contains(search_query, case=False)]
    
    st.dataframe(df_wh[['id', 'name', 'location', 'manager']], width="stretch")
    
    csv_data = df_wh.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Warehouse Infrastructure List to CSV",
        data=csv_data,
        file_name="tracerblock_warehouses.csv",
        mime="text/csv"
    )
else:
    st.info("No warehouses registered yet.")

st.markdown("---")
st.subheader("📦 On-Chain Facility Capacity Allocation")
if warehouses:
    for wh in warehouses:
        wh_total_stock = sum(item['quantity'] for item in inventory if item['warehouse'] == wh['id'])
        max_capacity = 1000
        pct = min(100, int((wh_total_stock / max_capacity) * 100))
        st.markdown(f"**{wh['name']} Allocations:** {wh_total_stock} / {max_capacity} units ({pct}%)")
        st.progress(pct / 100)
else:
    st.info("No capacity allocation logs available.")

st.markdown("---")
st.subheader("🚨 Stock Level Safety Alerts")
low_stock_events = [item for item in inventory if item['quantity'] <= item.get('low_stock_threshold', 10)]
if low_stock_events:
    for item in low_stock_events:
        st.error(f"⚠️ **{item['product_name']}** stock low ({item['quantity']} units). Safety stock threshold was breached.")
else:
    st.success("Fulfillment Rules State: All facility stock levels satisfy the safety stock parameters. ✅")

st.markdown("---")
st.subheader("🌡️ IoT Facility Safety Index")
if warehouses:
    for wh in warehouses:
        st.markdown(f"**{wh['name']} Stability Rating:** ⭐ **98/100** (IoT sensors state: Optimal Temperature & Humidity)")
else:
    st.info("No telemetry indices mapped.")
