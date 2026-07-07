import streamlit as st
import requests
import pandas as pd
try:
    from frontend.ui_components import load_custom_css, get_cached_data
except ModuleNotFoundError:
    from ui_components import load_custom_css, get_cached_data
import plotly.express as px
import os
import subprocess
import time
import sys

API_URL = os.environ.get("API_URL", "http://localhost:8000/api/")

def ensure_background_services():
    try:
        res = requests.get(f"{API_URL}supply_chain/products/", timeout=1)
        if res.status_code in [200, 401, 403]:
            return
    except Exception:
        pass
        
    print("[Streamlit Cloud] Port 8000 offline. Spawning background SCM environment...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    blockchain_script = os.path.join(base_dir, "scripts", "mock_blockchain.py")
    if os.path.exists(blockchain_script):
        subprocess.Popen([sys.executable, blockchain_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
    deploy_script = os.path.join(base_dir, "scripts", "deploy.py")
    if os.path.exists(deploy_script):
        subprocess.run([sys.executable, deploy_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    manage_script = os.path.join(base_dir, "backend", "manage.py")
    if os.path.exists(manage_script):
        subprocess.run([sys.executable, manage_script, "migrate"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([sys.executable, manage_script, "populate_db"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen([sys.executable, manage_script, "runserver", "127.0.0.1:8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

ensure_background_services()

st.set_page_config(page_title="TRACERBLOCK", layout="wide", page_icon="🔗")

if "token" not in st.session_state:
    st.session_state.token = None

def login():
    st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    <div class="login-mask"></div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-popup">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; color:#00f2fe; text-align:center;'>🔑 TRACERBLOCK Auth</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8; text-align:center; font-size:0.85rem;'>Security Access Lock & Secure Enclosure</p>", unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Unlock Portal & Decrypt Ledger", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Fields cannot be empty.")
                else:
                    try:
                        res = requests.post(f"{API_URL}token/", json={"username": username, "password": password})
                        if res.status_code == 200:
                            st.session_state.token = res.json()["access"]
                            st.session_state.pop("products_cache", None)
                            st.session_state.pop("inventory_cache", None)
                            st.session_state.pop("orders_cache", None)
                            st.session_state.pop("users_cache", None)
                            st.success("Authorized! ✅")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    except Exception as e:
                        st.error("Auth server offline. Start backend server first.")
                    
        st.markdown('</div>', unsafe_allow_html=True)

def dashboard():
    st.title("Executive Dashboard 📊")
    st.markdown("Real-time overview and analytical insights of the TRACERBLOCK supply chain.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    with st.spinner("🔒 Establishing secure handshake & decrypting SCM ledger records..."):
        try:
            products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
            inventory = get_cached_data(f"{API_URL}supply_chain/inventory/", "inventory_cache", headers)
            orders = get_cached_data(f"{API_URL}supply_chain/orders/", "orders_cache", headers)
        except Exception as e:
            st.error(f"Handshake failed: {e}")
            st.stop()
            
    try:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Registered Products", len(products))
        total_stock = sum(item['quantity'] for item in inventory)
        col2.metric("Total Stock (Units)", total_stock)
        col3.metric("Total Orders Placed", len(orders))
        
        st.markdown("---")
        
        recalled_ids = []
        for p in products:
            has_breach = False
            for ev in p.get('events', []):
                for tel in ev.get('telemetry', []):
                    if tel['temperature_c'] > 30 or tel['temperature_c'] < 2:
                        has_breach = True
            if has_breach:
                recalled_ids.append(f"{p['name']} (ID: {p['id']})")
                
        st.markdown("---")
        st.markdown("### Blockchain Safety Alerts")
        if recalled_ids:
            st.error(f"⚠️ **Solidity Contract Recall Triggered:** Cold-chain rules violated for the following items:")
            for item in recalled_ids:
                st.markdown(f"- **Recalled Product**: {item} - *Reason: On-Chain telemetry exceeded 2°C - 30°C range.*")
        else:
            st.success("Solidity Engine State: No on-chain recalls registered. All contract rules satisfied. ✅")

        st.markdown("### Interactive Filters & Analytics")
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            warehouses_list = list(set(item['warehouse_name'] for item in inventory))
            selected_wh = st.selectbox("Filter Inventory Chart by Warehouse", ["All"] + warehouses_list)
        
        with filter_col2:
            status_list = list(set(item['status'] for item in orders))
            selected_status = st.selectbox("Filter Orders by Status", ["All"] + status_list)

        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### Sunburst SCM Stock Distribution")
            sunburst_records = []
            for item in inventory:
                if selected_wh != "All" and item["warehouse_name"] != selected_wh:
                    continue
                prod_name = item["product_name"]
                prod_obj = next((p for p in products if p["id"] == item["product"]), None)
                category = "Industrial"
                if prod_obj and "description" in prod_obj:
                    desc = prod_obj["description"]
                    if desc.startswith("[") and "]" in desc:
                        category = desc.split("]")[0].replace("[", "")
                
                sunburst_records.append({
                    "Category": category,
                    "Warehouse": item["warehouse_name"],
                    "Product": prod_name,
                    "Quantity": item["quantity"]
                })
                
            if sunburst_records:
                df_sb = pd.DataFrame(sunburst_records)
                fig_sb = px.sunburst(df_sb, path=["Category", "Warehouse", "Product"], values="Quantity",
                                     color="Category",
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_sb.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_sb, width="stretch")
            else:
                st.info("No stock data for hierarchical distribution.")

        with chart_col2:
            if orders:
                df_ord = pd.DataFrame(orders)
                if selected_status != "All":
                    df_ord = df_ord[df_ord['status'] == selected_status]
                
                if not df_ord.empty:
                    status_counts = df_ord['status'].value_counts().reset_index()
                    status_counts.columns = ['Status', 'Count']
                    fig_ord = px.pie(status_counts, names='Status', values='Count', 
                                     title="Order Fulfillment Distribution",
                                     color_discrete_sequence=px.colors.qualitative.Safe)
                    fig_ord.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_ord, width="stretch")
                else:
                    st.info("No orders found matching the filter.")
            else:
                st.info("No order data available.")

        low_stock_items = [item for item in inventory if item['quantity'] <= item.get('low_stock_threshold', 10)]
        with st.expander("⚠️ Critical Stock Alerts & Reorder Advisor", expanded=True):
            if low_stock_items:
                st.warning("The following products are at or below their minimum safety stock threshold. Reordering is recommended.")
                df_low = pd.DataFrame(low_stock_items)[['product_name', 'warehouse_name', 'quantity', 'low_stock_threshold']]
                st.dataframe(df_low, width="stretch")
            else:
                st.success("All inventory levels are currently healthy and above safety thresholds! ✅")

        st.markdown("### Export Portal Data")
        if inventory:
            df_export = pd.DataFrame(inventory)
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Current Inventory to CSV",
                data=csv_data,
                file_name="tracerblock_inventory_report.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Could not connect to the API to fetch dashboard data: {e}")

if not st.session_state.token:
    login()
else:
    def logout():
        st.session_state.token = None
    st.sidebar.button("Logout", on_click=logout)
    dashboard()
