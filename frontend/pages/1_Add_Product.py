import streamlit as st
import requests
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

# Fetch warehouses dynamically (Optimized Buffering)
warehouses = get_cached_data(f"{API_URL}supply_chain/warehouses/", "warehouses_cache", headers)

wh_options = {"None": None}
for wh in warehouses:
    wh_options[f"{wh['name']} ({wh['location']})"] = wh['id']

# Main Form (Component 2)
with st.form("add_product_form"):
    col_a, col_b = st.columns(2)
    
    with col_a:
        name = st.text_input("Product Name", placeholder="e.g. Smart Watch Active") # Component 3
        category = st.selectbox("Product Category", ["Electronics", "Pharmaceuticals", "Food & Beverage", "Industrial", "Consumer Goods"]) # Component 4
        sku = st.text_input("SKU / Serial Code", placeholder="e.g. SKU-10029-A") # Component 5
        temp_req = st.slider("Safe Operating Temperature (°C)", -40, 60, (2, 30)) # Component 6
        
    with col_b:
        desc = st.text_area("Product Description", placeholder="Enter specifications, shipping constraints...") # Component 7
        wh_id = st.selectbox("Target Warehouse (for initial stock allocation)", list(wh_options.keys())) # Component 8
        initial_qty = st.number_input("Initial Inventory Quantity", min_value=0, value=0, step=10) # Component 9
        batch_no = st.text_input("Batch / Lot Number", placeholder="e.g. LOT-2026-07") # Component 10

    submit = st.form_submit_button("Register Product") # Component 11

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
                # Invalidate caches
                st.session_state.pop("products_cache", None)
                st.session_state.pop("inventory_cache", None)
                
                product_id = res.json()["id"]
                st.success(f"Product '{name}' successfully registered! (ID: {product_id}) ✅")
                
                # Automatically allocate initial stock if a warehouse is selected
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

# Bulk Upload Section with On-Chain Stager (Feature 3)
st.markdown("---")
st.subheader("📦 Bulk On-Chain CSV Stager")
uploaded_file = st.file_uploader("Upload product listings CSV for sequential on-chain staging", type=["csv"])
if uploaded_file is not None:
    st.info("Reading CSV records and calculating signatures...")
    import pandas as pd
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Staged products:")
        st.dataframe(df.head(5), width="stretch")
        if st.button("Commit Staged Batch to Blockchain"):
            # Simulate sequential mining
            for index, row in df.iterrows():
                st.code(f"Committing Row #{index+1}: {row.get('name', 'Product')} | Anchor: Anchored (Tx: 0x{index}aef...)")
            st.success("Batch successfully committed to mock blockchain ledger! ✅")
    except Exception as e:
        st.error(f"Error processing stager CSV: {e}")

# Blockchain Rule Parameters and Compilation (Feature 4)
st.markdown("---")
st.subheader("📜 On-Chain Rule Parameter Compiler")
with st.expander("Show Compiled Solidity Code Parameters"):
    st.code(f"""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SupplyChainRuleCheck {{
    // Automatically compiled parameters for {category or "Electronics"}
    int256 public constant MIN_TEMP = {temp_req[0]};
    int256 public constant MAX_TEMP = {temp_req[1]};
    string public constant CATEGORY = "{category}";
    string public constant SKU_CODE = "{sku}";
    
    function verifyTelemetry(int256 currentTemp) public pure returns (bool) {{
        return (currentTemp >= MIN_TEMP && currentTemp <= MAX_TEMP);
    }}
}}
    """, language="solidity")

# Draft Preview & Hash Anchoring (Features 1, 2, 5)
st.markdown("---")
st.subheader("🔍 Cryptographic Pre-Registration Anchor")

import hashlib
payload_str = f"{name}-{category}-{sku}-{desc}-{temp_req[0]}-{temp_req[1]}"
payload_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
manufacturer_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
mock_signature = "0x" + hashlib.sha256((payload_hash + manufacturer_address).encode('utf-8')).hexdigest()

estimated_gas = 142850
sim_gas_price_gwei = 20
total_gas_cost_eth = (estimated_gas * sim_gas_price_gwei) / 1e9
total_gas_cost_usd = total_gas_cost_eth * 3200.0

col_preview_1, col_preview_2 = st.columns(2)

with col_preview_1:
    st.markdown("#### Payload Metadata")
    draft_preview = {
        "Name": name,
        "Category": category,
        "SKU": sku,
        "Temp Limits": f"{temp_req[0]}°C to {temp_req[1]}°C",
        "Initial Units": initial_qty,
        "Batch": batch_no
    }
    st.json(draft_preview)

with col_preview_2:
    st.markdown("#### Cryptographic Properties")
    st.markdown(f"**SHA-256 Anchor Hash:**")
    st.code(payload_hash)
    st.markdown(f"**Manufacturer Public Key:**")
    st.code(manufacturer_address)
    st.markdown(f"**Digital Signature Hex:**")
    st.code(mock_signature[:35] + "...")
    
    st.markdown("#### Gas Cost Estimate")
    st.metric("Estimated Gas Fee", f"{total_gas_cost_eth:.6f} ETH (~${total_gas_cost_usd:.2f} USD)")
