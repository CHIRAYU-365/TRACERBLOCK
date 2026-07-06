import streamlit as st
import requests
from frontend.ui_components import load_custom_css
load_custom_css()

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000/api/")

if "token" not in st.session_state or not st.session_state.token:
    st.warning("Please login from the main page first.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("Order Management 📝")

st.subheader("Create Purchase Order")
with st.form("create_po_form"):
    buyer_id = st.number_input("Buyer (User ID)", min_value=1, step=1)
    seller_id = st.number_input("Seller (User ID)", min_value=1, step=1)
    prod_id = st.number_input("Product ID", min_value=1, step=1)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    submit_po = st.form_submit_button("Create PO")
    
    if submit_po:
        data = {
            "buyer": buyer_id,
            "seller": seller_id,
            "product": prod_id,
            "quantity": quantity,
            "status": "PENDING"
        }
        res = requests.post(f"{API_URL}supply_chain/orders/", json=data, headers=headers)
        if res.status_code == 201:
            st.success("Purchase Order Created! Escrow contract logic can be triggered here.")
        else:
            st.error("Failed to create PO. Check User and Product IDs.")

st.markdown("---")
st.subheader("All Orders")
ord_res = requests.get(f"{API_URL}supply_chain/orders/", headers=headers)
if ord_res.status_code == 200:
    st.dataframe(ord_res.json(), use_container_width=True)
