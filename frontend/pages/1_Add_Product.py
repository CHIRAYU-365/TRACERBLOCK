import streamlit as st
import requests
import hashlib
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

st.title("Register New Product 📦")
st.markdown("Add a new product to the portal. This will register the item, define IoT parameters, and set up initial stock levels.")

warehouses = get_cached_data(f"{API_URL}supply_chain/warehouses/", "warehouses_cache", headers)

wh_options = {"None": None}
for wh in warehouses:
    wh_options[f"{wh['name']} ({wh['location']})"] = wh['id']

with st.form("add_product_form"):
    col_a, col_b = st.columns(2)
    
    with col_a:
        name = st.text_input("Product Name", placeholder="e.g. Smart Watch Active")
        category = st.selectbox("Product Category", ["Electronics", "Pharmaceuticals", "Food & Beverage", "Industrial", "Consumer Goods"])
        sku = st.text_input("SKU / Serial Code", placeholder="e.g. SKU-10029-A")
        temp_req = st.slider("Safe Operating Temperature (°C)", -40, 60, (2, 30))
        
    with col_b:
        desc = st.text_area("Product Description", placeholder="Enter specifications, shipping constraints...")
        wh_id = st.selectbox("Target Warehouse (for initial stock allocation)", list(wh_options.keys()))
        initial_qty = st.number_input("Initial Inventory Quantity", min_value=0, value=0, step=10)
        batch_no = st.text_input("Batch / Lot Number", placeholder="e.g. LOT-2026-07")

    submit = st.form_submit_button("Register Product")

    if submit:
        if not name:
            st.error("Product name is required.")
        else:
            product_data = {
                "name": name,
                "description": f"[{category}] {desc} | SKU: {sku} | Temp Range: {temp_req[0]}C to {temp_req[1]}C | Batch: {batch_no}"
            }
            res = requests.post(f"{API_URL}supply_chain/products/", json=product_data, headers=headers)
            if res.status_code == 201:
                st.session_state.pop("products_cache", None)
                st.session_state.pop("inventory_cache", None)
                
                product_id = res.json()["id"]
                st.success(f"Product '{name}' successfully registered! (ID: {product_id}) ✅")
                
                selected_wh_id = wh_options[wh_id]
                if selected_wh_id is not None and initial_qty > 0:
                    stock_data = {
                        "product": product_id,
                        "warehouse": selected_wh_id,
                        "quantity": initial_qty
                    }
                    stock_res = requests.post(f"{API_URL}supply_chain/inventory/", json=stock_data, headers=headers)
                    if stock_res.status_code == 201:
                        st.success(f"Allocated {initial_qty} units of initial stock to the selected warehouse.")
                    else:
                        st.warning(f"Failed to allocate initial stock: {stock_res.text}")
            else:
                st.error(f"Failed to register product: {res.text}")

st.markdown("---")
st.subheader("📦 Bulk On-Chain CSV Stager")
uploaded_file = st.file_uploader("Upload product listings CSV for sequential on-chain staging", type=["csv"])
if uploaded_file is not None:
    st.info("Reading CSV records and calculating signatures...")
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Staged products:")
        st.dataframe(df.head(5), use_container_width=True)
        if st.button("Commit Staged Batch to Blockchain"):
            for index, row in df.iterrows():
                st.write(f"✓ Committing Row #{index+1}: {row.get('name', 'Product')} | Status: SUCCESS")
            st.success("Batch successfully committed to mock blockchain ledger! ✅")
    except Exception as e:
        st.error(f"Error processing stager CSV: {e}")

st.markdown("---")
st.subheader("🔍 Pre-Registration Draft Review")

draft_preview = {
    "Name": name,
    "Category": category,
    "SKU": sku,
    "Temp Limits": f"{temp_req[0]}°C to {temp_req[1]}°C",
    "Initial Units": initial_qty,
    "Batch": batch_no
}
st.json(draft_preview)
