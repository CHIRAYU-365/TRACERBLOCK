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

st.title("Register New Product 📦")

with st.form("add_product_form"):
    name = st.text_input("Product Name")
    desc = st.text_area("Description")
    submit = st.form_submit_button("Register Product")
    
    if submit:
        data = {"name": name, "description": desc}
        res = requests.post(f"{API_URL}supply_chain/products/", json=data, headers=headers)
        if res.status_code == 201:
            st.success("Product registered successfully! ✅")
        else:
            st.error(f"Failed to register: {res.text}")
