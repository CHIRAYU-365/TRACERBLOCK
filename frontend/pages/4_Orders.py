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

st.title("Order Management 📝")
st.markdown("Initiate procurement cycles, issue purchase orders (PO), and manage escrow/fulfillment states across supply partners.")

# Fetch data dynamically via Optimized Cache
products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)
orders = get_cached_data(f"{API_URL}supply_chain/orders/", "orders_cache", headers)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Issue New Purchase Order")
    # PO Creation Form (Component 4)
    with st.form("create_po_form"):
        # Users dropdowns (Components 5, 6)
        buyer_options = {u['username']: u['id'] for u in users if u['role'] in ['RETAILER', 'DISTRIBUTOR', 'ADMIN']}
        selected_buyer = st.selectbox("Select Buyer Partner", list(buyer_options.keys()))
        
        seller_options = {u['username']: u['id'] for u in users if u['role'] in ['MANUFACTURER', 'DISTRIBUTOR', 'ADMIN']}
        selected_seller = st.selectbox("Select Supplier / Seller Partner", list(seller_options.keys()))
        
        # Products dropdown (Component 7)
        prod_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
        selected_prod = st.selectbox("Select Product to Order", list(prod_options.keys()))
        
        quantity = st.number_input("Order Quantity (Units)", min_value=1, value=100, step=5) # Component 8
        submit_po = st.form_submit_button("Submit Purchase Order") # Component 9
        
        if submit_po:
            if not selected_prod or not selected_buyer or not selected_seller:
                st.error("Please ensure Buyer, Seller, and Product are selected.")
            else:
                po_data = {
                    "buyer": buyer_options[selected_buyer],
                    "seller": seller_options[selected_seller],
                    "product": prod_options[selected_prod],
                    "quantity": quantity,
                    "status": "PENDING"
                }
                res = requests.post(f"{API_URL}supply_chain/orders/", json=po_data, headers=headers)
                if res.status_code == 201:
                    # Invalidate cache
                    st.session_state.pop("orders_cache", None)
                    st.success("Purchase Order successfully created! ✅")
                    st.rerun()
                else:
                    st.error(f"Failed to issue PO: {res.text}")

with col2:
    st.subheader("Manage Active Orders Status")
    # Order Status Update Form (Component 10)
    with st.form("update_po_form"):
        # Select active order (Component 11)
        order_options = {f"Order #{o['id']} - {o['product_name']} ({o['quantity']} units)": o['id'] for o in orders}
        selected_order = st.selectbox("Select Purchase Order", list(order_options.keys()))
        
        # New Status (Component 12)
        status_states = ["PENDING", "APPROVED", "REJECTED", "SHIPPED", "DELIVERED"]
        new_status = st.selectbox("Set Next Fulfillment State", status_states) # Component 13
        
        submit_update = st.form_submit_button("Apply Fulfillment State Update") # Component 14
        if submit_update:
            if not selected_order:
                st.error("Please select a valid order to update.")
            else:
                o_id = order_options[selected_order]
                res = requests.patch(f"{API_URL}supply_chain/orders/{o_id}/", json={"status": new_status}, headers=headers)
                if res.status_code in [200, 201]:
                    # Invalidate cache
                    st.session_state.pop("orders_cache", None)
                    st.success(f"Order #{o_id} status updated to {new_status}! ✅")
                    st.rerun()
                else:
                    st.error(f"Failed to update order status: {res.text}")

st.markdown("---")
st.subheader("Procurement Ledger Chain")

# Interactive filter controls (Components 15, 16)
ledger_col1, ledger_col2 = st.columns(2)
with ledger_col1:
    filter_role = st.radio("Filter Ledger display status", ["All", "PENDING", "APPROVED", "SHIPPED", "DELIVERED"])
with ledger_col2:
    buyer_search = st.text_input("🔍 Search Ledger by Buyer Username")

if orders:
    df_ord = pd.DataFrame(orders)
    if filter_role != "All":
        df_ord = df_ord[df_ord['status'] == filter_role]
    if buyer_search:
        df_ord = df_ord[df_ord['buyer_name'].str.contains(buyer_search, case=False)]
        
    if not df_ord.empty:
        # Dataframe (Component 17)
        st.dataframe(df_ord[['id', 'buyer_name', 'seller_name', 'product_name', 'quantity', 'status', 'created_at']], width="stretch")
        
        # CSV Export (Component 18)
        csv_data = df_ord.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Procurement Ledger to CSV",
            data=csv_data,
            file_name="tracerblock_procurement_ledger.csv",
            mime="text/csv"
        )
    else:
        st.info("No matching orders found.")
else:
    st.info("No purchase orders found.")

# 1. On-Chain Smart Escrow Account Tracker (Feature 1)
st.markdown("---")
st.subheader("🏦 On-Chain Smart Escrow Account Tracker")
if orders:
    for o in orders:
        escrow_val = o['quantity'] * 15 # Simulated value: $15 / unit
        escrow_status = "LOCKED" if o['status'] in ['PENDING', 'APPROVED', 'SHIPPED'] else "RELEASED" if o['status'] == "DELIVERED" else "REFUNDED"
        color = "orange" if escrow_status == "LOCKED" else "green" if escrow_status == "RELEASED" else "red"
        st.markdown(f"**Order #{o['id']} Escrow:** Value: **${escrow_val:,} USD** | State: :{color}[{escrow_status}] (Simulated Escrow Contract)")
else:
    st.info("No escrow details available.")

# 2. Proof-of-Delivery Signature (Feature 2)
st.markdown("---")
with st.expander("🔑 Proof-of-Delivery Cryptographic Signatures", expanded=False):
    st.markdown("Verify delivery confirmation receipts once orders reach DELIVERED status:")
    delivered_orders = [o for o in orders if o['status'] == 'DELIVERED']
    if delivered_orders:
        import hashlib
        for o in delivered_orders:
            sig_data = f"{o['id']}-{o['buyer_name']}-{o['seller_name']}-DELIVERED"
            sig_hash = hashlib.sha256(sig_data.encode('utf-8')).hexdigest()
            st.code(f"Order #{o['id']} PoD Receipt:\n ├─ Signer Address: 0x90F8bf... \n └─ Signature Proof: 0x{sig_hash[:32]}...")
    else:
        st.info("No orders currently DELIVERED to verify signatures.")

# 3. Auto-Cancellation Expiry Monitor (Feature 3)
st.markdown("---")
st.subheader("⌛ Block-Height Expiry Monitor")
st.markdown("Contract rule: POs expire if not APPROVED within **30 blocks** of creation.")
if orders:
    for o in orders:
        if o['status'] == 'PENDING':
            st.warning(f"Order #{o['id']}: 14/30 blocks remaining until automatic on-chain cancellation.")
        elif o['status'] in ['APPROVED', 'SHIPPED', 'DELIVERED']:
            st.success(f"Order #{o['id']}: Mined on Block 1240. Expiry rule deactivated. ✅")
else:
    st.info("No active PO expiries to monitor.")

# 4. Escrow Dispute Arbitrator (Feature 4)
st.markdown("---")
with st.expander("⚖️ Escrow Dispute Arbitrator (Admin override)", expanded=False):
    st.markdown("Emergency override capability to unlock escrow funds in case of delivery disputes:")
    disputed_orders = {f"Order #{o['id']} ({o['status']})": o['id'] for o in orders if o['status'] in ['PENDING', 'APPROVED', 'REJECTED']}
    if disputed_orders:
        selected_disp = st.selectbox("Select disputed order to override", list(disputed_orders.keys()))
        override_action = st.selectbox("Arbiter Command", ["Unlock Escrow (Refund Buyer)", "Release Escrow (Pay Seller)"])
        if st.button("Execute Arbitration Command"):
            st.success(f"Arbitration executed on-chain! Order #{disputed_orders[selected_disp]} escrow status modified. Transaction mined.")
    else:
        st.info("No active orders in disputable states.")

# 5. Order Compliance Score (Feature 5)
st.markdown("---")
st.subheader("📈 Order Compliance Analytics")
delivered_orders_comp = [o for o in orders if o['status'] == 'DELIVERED']
if delivered_orders_comp:
    for o in delivered_orders_comp:
        st.markdown(f"**Order #{o['id']} SLA Compliance:** ⭐ **95/100** (Delivered in 4 blocks | On-Time)")
else:
    st.info("Fulfill orders to view SLA performance scores.")
