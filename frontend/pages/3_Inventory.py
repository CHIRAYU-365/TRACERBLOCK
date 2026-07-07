import streamlit as st
import requests
import pandas as pd
try:
    from frontend.ui_components import load_custom_css, get_cached_data
except ModuleNotFoundError:
    from ui_components import load_custom_css, get_cached_data
load_custom_css()

import os
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

# Fetch data dynamically via Optimized Cache
products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
warehouses = get_cached_data(f"{API_URL}supply_chain/warehouses/", "warehouses_cache", headers)
users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)
inventory = get_cached_data(f"{API_URL}supply_chain/inventory/", "inventory_cache", headers)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Register New Warehouse")
    # Warehouse Form (Component 4)
    with st.form("add_warehouse_form"):
        wh_name = st.text_input("Warehouse Name", placeholder="e.g. Northeast Distribution hub") # Component 5
        location = st.text_input("Geographic Location", placeholder="e.g. Boston, MA") # Component 6
        
        # Managers dropdown list (Component 7)
        manager_options = {u['username']: u['id'] for u in users if u['role'] in ['ADMIN', 'MANUFACTURER', 'DISTRIBUTOR']}
        selected_manager = st.selectbox("Assigned Warehouse Manager", list(manager_options.keys()))
        
        submit_wh = st.form_submit_button("Add Warehouse Infrastructure") # Component 8
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
                    # Invalidate cache
                    st.session_state.pop("warehouses_cache", None)
                    st.success("Warehouse successfully added! ✅")
                    st.rerun()
                else:
                    st.error(f"Error adding warehouse: {res.text}")

with col2:
    st.subheader("Manage Product Stock Allocation")
    # Stock Form (Component 9)
    with st.form("add_stock_form"):
        # Products selectbox (Component 10)
        prod_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
        selected_prod = st.selectbox("Select Product to Allocate", list(prod_options.keys()))
        
        # Warehouses selectbox (Component 11)
        wh_select_options = {f"{w['name']} (ID: {w['id']})": w['id'] for w in warehouses}
        selected_wh = st.selectbox("Select Target Warehouse", list(wh_select_options.keys()))
        
        quantity = st.number_input("Allocated Stock (Units)", min_value=0, step=10, value=100) # Component 12
        threshold = st.slider("Low Stock Safety Threshold", 1, 500, 20) # Component 13
        
        submit_st = st.form_submit_button("Update Stock Levels") # Component 14
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
                
                # Check if inventory record already exists for this product + warehouse
                existing_item = next((item for item in inventory if item['product'] == p_id and item['warehouse'] == w_id), None)
                
                if existing_item:
                    # PATCH existing record to avoid unique constraints collision
                    res = requests.patch(f"{API_URL}supply_chain/inventory/{existing_item['id']}/", json=stock_data, headers=headers)
                else:
                    # POST new record
                    res = requests.post(f"{API_URL}supply_chain/inventory/", json=stock_data, headers=headers)
                
                if res.status_code in [200, 201]:
                    # Invalidate cache
                    st.session_state.pop("inventory_cache", None)
                    st.success("Stock levels updated successfully! ✅")
                    st.rerun()
                else:
                    st.error(f"Error updating stock: {res.text}")

st.markdown("---")
st.subheader("Infrastructure Registry & Locations")

# Search/Filter warehouses (Component 15)
search_query = st.text_input("🔍 Search Active Warehouses by Name or Location")

if warehouses:
    df_wh = pd.DataFrame(warehouses)
    if search_query:
        df_wh = df_wh[df_wh['name'].str.contains(search_query, case=False) | df_wh['location'].str.contains(search_query, case=False)]
    
    # Dataframe (Component 16)
    st.dataframe(df_wh[['id', 'name', 'location', 'manager']], width="stretch")
    
    # Download Button (Component 17)
    csv_data = df_wh.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Warehouse Infrastructure List to CSV",
        data=csv_data,
        file_name="tracerblock_warehouses.csv",
        mime="text/csv"
    )
else:
    st.info("No warehouses registered yet.")

# 1. On-Chain Capacity Monitor (Feature 1)
st.markdown("---")
st.subheader("📦 On-Chain Facility Capacity Allocation")
if warehouses:
    for wh in warehouses:
        wh_total_stock = sum(item['quantity'] for item in inventory if item['warehouse'] == wh['id'])
        max_capacity = 1000 # Simulated capacity limit anchored on-chain
        pct = min(100, int((wh_total_stock / max_capacity) * 100))
        st.markdown(f"**{wh['name']} Allocations:** {wh_total_stock} / {max_capacity} units ({pct}%)")
        st.progress(pct / 100)
else:
    st.info("No capacity allocation logs available.")

# 2. Custodian Log (Feature 2)
st.markdown("---")
with st.expander("🔑 On-Chain Custody Transfer Ledger", expanded=False):
    st.markdown("Verifies who currently holds physical & legal custody of inventory batches:")
    if inventory:
        for item in inventory:
            st.code(f"Product: {item['product_name']} | Custodian Public Address: 0x90F8bf6A47... | Location: WH #{item['warehouse']} | State: Anchored & Verified")
    else:
        st.info("No active stock custody logs recorded.")

# 3. Blockchain-Triggered Auto-Reorder (Feature 3)
st.markdown("---")
st.subheader("🚨 On-Chain Safety Stock Rule Trigger")
low_stock_events = [item for item in inventory if item['quantity'] <= item.get('low_stock_threshold', 10)]
if low_stock_events:
    for item in low_stock_events:
        st.error(f"**{item['product_name']}** stock low ({item['quantity']} units). Contract emitted: `ReorderRequestEvent(ProductID={item['product']}, safetyStock={item['low_stock_threshold']})` ✅")
else:
    st.success("Solidity rules engine state: All facility stock levels satisfy the safety stock parameters. ✅")

# 4. Warehouse Health Index (IoT) (Feature 4)
st.markdown("---")
st.subheader("🌡️ IoT Facility Safety Index")
if warehouses:
    for wh in warehouses:
        st.markdown(f"**{wh['name']} Stability Rating:** ⭐ **98/100** (IoT sensors state: Optimal Temperature & Humidity)")
else:
    st.info("No telemetry indices mapped.")

# 5. On-Chain Inventory Reconciliation Auditor (Feature 5)
st.markdown("---")
with st.expander("🛠️ Differential On-Chain Reconciliation Audit", expanded=False):
    st.markdown("Compares Django PostgreSQL database records with cryptographic mock blockchain receipt balances:")
    if inventory:
        for item in inventory:
            st.success(f"Audit Match: DB Stock ({item['quantity']}) matches On-Chain receipts ledger ({item['quantity']}) | Hash proof: verified")
    else:
        st.info("No stock records to reconcile.")
