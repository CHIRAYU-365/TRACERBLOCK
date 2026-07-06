import streamlit as st
import requests
import pandas as pd
from frontend.ui_components import load_custom_css
import plotly.express as px

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000/api/")

st.set_page_config(page_title="TRACERBLOCK", layout="wide", page_icon="🔗")

if "token" not in st.session_state:
    st.session_state.token = None

def login():
    st.title("Login to TRACERBLOCK 🔐")
    st.markdown("Enter your credentials to access the enterprise SCM portal.")
    
    st.info("💡 **Hint:** If you haven't created a user yet, run `python backend/manage.py createsuperuser`.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        if submit:
            try:
                res = requests.post(f"{API_URL}token/", json={"username": username, "password": password})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access"]
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error("Could not connect to the authentication server. Ensure Django is running.")

def dashboard():
    st.title("Executive Dashboard 📊")
    st.markdown("Overview of Supply Chain Health")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    try:
        col1, col2, col3 = st.columns(3)
        
        # Products
        prod_res = requests.get(f"{API_URL}supply_chain/products/", headers=headers)
        if prod_res.status_code == 200:
            products = prod_res.json()
            col1.metric("Total Products", len(products))
        
        # Inventory
        inv_res = requests.get(f"{API_URL}supply_chain/inventory/", headers=headers)
        if inv_res.status_code == 200:
            inventory = inv_res.json()
            total_stock = sum(item['quantity'] for item in inventory)
            col2.metric("Total Stock (Units)", total_stock)
            
            if inventory:
                df_inv = pd.DataFrame(inventory)
                fig_inv = px.bar(df_inv, x='warehouse_name', y='quantity', color='product_name', title="Stock by Warehouse")
                st.plotly_chart(fig_inv, use_container_width=True)
                
        # Orders
        ord_res = requests.get(f"{API_URL}supply_chain/orders/", headers=headers)
        if ord_res.status_code == 200:
            orders = ord_res.json()
            col3.metric("Total Orders", len(orders))
            
            if orders:
                df_ord = pd.DataFrame(orders)
                status_counts = df_ord['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                fig_ord = px.pie(status_counts, names='Status', values='Count', title="Order Fulfillment Status")
                st.plotly_chart(fig_ord, use_container_width=True)
                
    except Exception as e:
        st.error("Could not connect to the API to fetch dashboard data.")

if not st.session_state.token:
    login()
else:
    def logout():
        st.session_state.token = None
    st.sidebar.button("Logout", on_click=logout)
    dashboard()
