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

st.title("Inventory Management 🏢")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Add Warehouse")
    with st.form("add_warehouse_form"):
        name = st.text_input("Warehouse Name")
        location = st.text_input("Location")
        submit_wh = st.form_submit_button("Add Warehouse")
        if submit_wh:
            res = requests.post(f"{API_URL}supply_chain/warehouses/", json={"name": name, "location": location}, headers=headers)
            if res.status_code == 201:
                st.success("Warehouse added!")
            else:
                st.error("Error adding warehouse")

with col2:
    st.subheader("Add Stock")
    with st.form("add_stock_form"):
        prod_id = st.number_input("Product ID", min_value=1, step=1)
        wh_id = st.number_input("Warehouse ID", min_value=1, step=1)
        quantity = st.number_input("Quantity", min_value=0, step=10)
        submit_st = st.form_submit_button("Update Stock")
        if submit_st:
            data = {"product": prod_id, "warehouse": wh_id, "quantity": quantity}
            res = requests.post(f"{API_URL}supply_chain/inventory/", json=data, headers=headers)
            if res.status_code == 201:
                st.success("Stock updated!")
            else:
                st.error("Error updating stock. Ensure Product and Warehouse IDs exist.")

st.markdown("---")
st.subheader("Current Warehouses")
wh_res = requests.get(f"{API_URL}supply_chain/warehouses/", headers=headers)
if wh_res.status_code == 200:
    st.dataframe(wh_res.json(), use_container_width=True)
