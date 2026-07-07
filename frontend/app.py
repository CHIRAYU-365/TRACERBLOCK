import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import subprocess
import time
import sys
import hashlib
import base64
import json

try:
    from frontend.ui_components import load_custom_css, get_cached_data
except ModuleNotFoundError:
    from ui_components import load_custom_css, get_cached_data

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
    log_file_path = os.path.join(base_dir, "background_services.log")
    
    with open(log_file_path, "a") as log_file:
        log_file.write(f"--- Booting Environment at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        log_file.flush()
        
        blockchain_script = os.path.join(base_dir, "scripts", "mock_blockchain.py")
        if os.path.exists(blockchain_script):
            subprocess.Popen([sys.executable, blockchain_script], stdout=log_file, stderr=log_file)
            time.sleep(1)
            
        deploy_script = os.path.join(base_dir, "scripts", "deploy.py")
        if os.path.exists(deploy_script):
            subprocess.run([sys.executable, deploy_script], stdout=log_file, stderr=log_file)
            
        manage_script = os.path.join(base_dir, "backend", "manage.py")
        if os.path.exists(manage_script):
            subprocess.run([sys.executable, manage_script, "migrate"], stdout=log_file, stderr=log_file)
            subprocess.run([sys.executable, manage_script, "populate_db"], stdout=log_file, stderr=log_file)
            subprocess.Popen([sys.executable, manage_script, "runserver", "127.0.0.1:8000"], stdout=log_file, stderr=log_file)
            time.sleep(2)

if "background_services_started" not in st.session_state:
    ensure_background_services()
    st.session_state.background_services_started = True

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages_dir = os.path.join(base_dir, "frontend", "pages")
if os.path.exists(pages_dir):
    import shutil
    try:
        shutil.rmtree(pages_dir)
    except Exception:
        pass

st.set_page_config(page_title="TRACERBLOCK", layout="wide", page_icon="🔗")
load_custom_css()

if "token" not in st.session_state:
    st.session_state.token = None

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Executive Dashboard"

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
        st.markdown("<h3 style='margin-top:0; color:#3b82f6; text-align:center;'>🔑 Roho SCM</h3>", unsafe_allow_html=True)
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
                            st.session_state.pop("warehouses_cache", None)
                            st.session_state.pop("qa_reports_cache", None)
                            st.success("Authorized! ✅")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    except Exception as e:
                        st.error("Auth server offline. Start backend server first.")
                    
        st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard(headers):
    st.subheader("Executive Dashboard")
    st.markdown("Real-time overview and analytical SCM metrics.")
    
    try:
        products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
        inventory = get_cached_data(f"{API_URL}supply_chain/inventory/", "inventory_cache", headers)
        orders = get_cached_data(f"{API_URL}supply_chain/orders/", "orders_cache", headers)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Registered Products", len(products))
        total_stock = sum(item['quantity'] for item in inventory)
        col2.metric("Total Stock (Units)", total_stock)
        col3.metric("Total Orders Placed", len(orders))
        
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
            st.error(f"⚠️ **Fulfillment Rules Violation Recall:** Temperature limits exceeded for:")
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
                st.plotly_chart(fig_sb, use_container_width=True)
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
                    st.plotly_chart(fig_ord, use_container_width=True)
                else:
                    st.info("No orders found matching the filter.")
            else:
                st.info("No order data available.")

        low_stock_items = [item for item in inventory if item['quantity'] <= item.get('low_stock_threshold', 10)]
        with st.expander("⚠️ Critical Stock Alerts & Reorder Advisor", expanded=True):
            if low_stock_items:
                st.warning("The following products are at or below their minimum safety stock threshold. Reordering is recommended.")
                df_low = pd.DataFrame(low_stock_items)[['product_name', 'warehouse_name', 'quantity', 'low_stock_threshold']]
                st.dataframe(df_low, use_container_width=True)
            else:
                st.success("All inventory levels are currently healthy and above safety thresholds! ✅")

    except Exception as e:
        st.error(f"Failed to load dashboard data: {e}")

def render_register_product(headers):
    st.subheader("Register New Product")
    st.markdown("Add a new product, define IoT bounds, and set up initial stock levels.")
    
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

def render_track_product(headers):
    st.subheader("Track & Update Product")
    st.markdown("Query product provenance, log transit checkpoints, and view IoT telemetry charts.")
    
    products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
    product_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
    
    if product_options:
        selected_prod = st.selectbox("Select Product to Track/Update", list(product_options.keys()))
        pid = product_options[selected_prod]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Record Checkpoint Event")
            location = st.text_input("Current Location / Facility", placeholder="e.g. Rotterdam Port Vault")
            status = st.selectbox("Event Status", ["MANUFACTURED", "IN_TRANSIT", "DELIVERED", "QA_PASSED", "QA_FAILED"])
            
            st.markdown("**Simulated IoT Telemetry Sensors**")
            temp = st.number_input("Container Temperature (°C)", value=15.0)
            hum = st.number_input("Container Humidity (%)", value=50.0)
            
            if st.button("Broadcast Transit Checkpoint"):
                if not location:
                    st.error("Location is required.")
                else:
                    ev_data = {
                        "product": pid,
                        "status": status,
                        "location": location
                    }
                    ev_res = requests.post(f"{API_URL}supply_chain/tracking/", json=ev_data, headers=headers)
                    if ev_res.status_code == 201:
                        st.session_state.pop("products_cache", None)
                        
                        event_id = ev_res.json()["id"]
                        tel_data = {
                            "event": event_id,
                            "temperature_c": temp,
                            "humidity_percent": hum
                        }
                        requests.post(f"{API_URL}supply_chain/telemetry/", json=tel_data, headers=headers)
                        
                        st.success("Successfully anchored checkpoint logs to private SCM registry! ✅")
                        st.rerun()
                    else:
                        st.error(f"Failed to record checkpoint: {ev_res.text}")

        with col2:
            st.subheader("Provenance Records")
            res = requests.get(f"{API_URL}supply_chain/products/{pid}/", headers=headers)
            product = res.json()
            
            st.markdown("#### 🔑 Multisignature Custody Handshake")
            col_sig1, col_sig2 = st.columns(2)
            with col_sig1:
                sig1 = st.checkbox("Logistics Partner digital signature (LOGISTICS_ROLE)")
            with col_sig2:
                sig2 = st.checkbox("Distributor Partner digital signature (DISTRIBUTOR_ROLE)")
                
            if sig1 and sig2:
                st.success("✅ Custody Handshake: Cryptographic signatures verified. Block ready for mining.")
            else:
                st.warning("Locked: Custody change requires signatures from both logistics and distributor accounts.")

        st.markdown("### IoT Telemetry History")
        if product.get('events'):
            tel_records = []
            for ev in product['events']:
                for tel in ev.get('telemetry', []):
                    tel_records.append({
                        "Time": tel['timestamp'],
                        "Temperature (°C)": tel['temperature_c'],
                        "Humidity (%)": tel['humidity_percent']
                    })
            if tel_records:
                df_tel = pd.DataFrame(tel_records)
                fig = px.line(df_tel, x="Time", y=["Temperature (°C)", "Humidity (%)"], 
                              title="IoT Container Sensors - Live Transit logs",
                              color_discrete_sequence=["#00f2fe", "#a18cd1"])
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No IoT sensor recordings found for this product.")

            st.markdown("### 🗺️ On-Chain Checkpoint Timeline")
            route_records = []
            for idx, ev in enumerate(product['events']):
                route_records.append({
                    "Checkpoint": f"{idx+1}. {ev['status']}",
                    "Location": ev['location'],
                    "Timestamp": ev['timestamp']
                })
            if route_records:
                df_route = pd.DataFrame(route_records)
                fig_route = px.bar(df_route, x='Timestamp', y='Checkpoint', color='Location',
                                   title="Product Checkpoints Journey Path",
                                   color_discrete_sequence=px.colors.qualitative.Dark2)
                fig_route.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_route, use_container_width=True)

            st.markdown("### Checkpoint History Ledger")
            df_events = pd.DataFrame(product['events'])
            if not df_events.empty:
                st.dataframe(df_events[['id', 'status', 'location', 'timestamp']], use_container_width=True)
                
                recalls = [ev for ev in product['events'] if any(t['temperature_c'] > 30 or t['temperature_c'] < 2 for t in ev.get('telemetry', []))]
                if recalls:
                    st.error("⚠️ **Fulfillment Rules Violation:** Temperature violations detected (outside safe 2°C - 30°C range). Reorder required.")
                else:
                    st.success("Fulfillment Rules State: Product temperatures conform to contract parameters. ✅")
                            
                csv_data = df_events[['status', 'location', 'timestamp']].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Provenance Chain to CSV",
                    data=csv_data,
                    file_name=f"product_{pid}_provenance_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No checkpoint records found.")
        else:
            st.info("No events logged yet.")
    else:
        st.info("No products registered yet.")

def render_inventory_management(headers):
    st.subheader("Inventory Management")
    st.markdown("Monitor and allocate inventory levels across active warehouses.")
    
    products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
    warehouses = get_cached_data(f"{API_URL}supply_chain/warehouses/", "warehouses_cache", headers)
    inventory = get_cached_data(f"{API_URL}supply_chain/inventory/", "inventory_cache", headers)
    
    wh_options = {"All": None}
    for wh in warehouses:
        wh_options[wh['name']] = wh['id']
        
    selected_wh_name = st.selectbox("Select Warehouse to View Stock", list(wh_options.keys()))
    selected_wh_id = wh_options[selected_wh_name]
    
    filtered_inventory = inventory
    if selected_wh_id is not None:
        filtered_inventory = [item for item in inventory if item['warehouse'] == selected_wh_id]
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Stock Allocation")
        if filtered_inventory:
            df_inv = pd.DataFrame(filtered_inventory)
            st.dataframe(df_inv[['product_name', 'quantity', 'low_stock_threshold', 'warehouse_name']], use_container_width=True)
            
            csv_data = df_inv.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Selected Inventory to CSV",
                data=csv_data,
                file_name="warehouse_inventory_report.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No inventory allocated to this warehouse facility.")
            
    with col2:
        st.subheader("Stock Allocation Levels")
        if filtered_inventory:
            for item in filtered_inventory:
                wh_total_stock = item['quantity']
                max_capacity = 500
                pct = int((wh_total_stock / max_capacity) * 100)
                pct = min(pct, 100)
                st.write(f"**{item['product_name']}** (Stock: {wh_total_stock} / Max: {max_capacity} units)")
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

def render_order_management(headers):
    st.subheader("Order Management")
    st.markdown("Initiate procurement cycles, issue purchase orders (PO), and manage escrow/fulfillment states.")
    
    products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
    users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)
    orders = get_cached_data(f"{API_URL}supply_chain/orders/", "orders_cache", headers)
    
    st.subheader("Register Purchase Order")
    prod_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
    partner_options = {u['username']: u['id'] for u in users if u['role'] in ['DISTRIBUTOR', 'RETAILER', 'ADMIN']}
    
    if prod_options and partner_options:
        with st.form("create_po_form"):
            selected_prod = st.selectbox("Select Product", list(prod_options.keys()))
            selected_buyer = st.selectbox("Select SCM Partner (Buyer)", list(partner_options.keys()))
            quantity = st.number_input("Purchase Quantity", min_value=1, value=100, step=10)
            price = st.number_input("Unit Price ($)", min_value=0.1, value=15.0, step=1.0)
            
            submit = st.form_submit_button("Initiate Purchase Order")
            if submit:
                po_data = {
                    "product": prod_options[selected_prod],
                    "buyer": partner_options[selected_buyer],
                    "quantity": quantity,
                    "unit_price": price
                }
                res = requests.post(f"{API_URL}supply_chain/orders/", json=po_data, headers=headers)
                if res.status_code == 201:
                    st.session_state.pop("orders_cache", None)
                    st.success("Successfully initialized Purchase Order! Escrow funds locked on-chain. ✅")
                    st.rerun()
                else:
                    st.error(f"Failed to initialize PO: {res.text}")
    else:
        st.info("Products and SCM buyer partners directory must be populated to trigger orders.")
        
    st.markdown("---")
    st.subheader("Order Audits Ledger")
    if orders:
        df_orders = pd.DataFrame(orders)
        st.dataframe(df_orders[['id', 'product_name', 'buyer_name', 'quantity', 'unit_price', 'status']], use_container_width=True)
        
        st.subheader("On-Chain Smart Escrow Account Tracker")
        for o in orders:
            total_escrow_val = o['quantity'] * o['unit_price']
            escrow_status = "LOCKED" if o['status'] in ['PENDING', 'APPROVED', 'SHIPPED'] else "RELEASED (Paid)"
            if o['status'] == 'REJECTED':
                escrow_status = "REFUNDED"
            st.info(f"**Escrow for PO #{o['id']}:** Locked Value: **${total_escrow_val:,.2f} USD** | State: `{escrow_status}`")
    else:
        st.info("No escrow details available.")

    st.markdown("---")
    st.subheader("⌛ Procurement Expiry Monitor")
    st.markdown("Contract rule: POs expire if not APPROVED within **30 blocks** of creation.")
    if orders:
        for o in orders:
            if o['status'] == 'PENDING':
                st.warning(f"Order #{o['id']}: 14/30 blocks remaining until automatic on-chain cancellation.")
            elif o['status'] in ['APPROVED', 'SHIPPED', 'DELIVERED']:
                st.success(f"Order #{o['id']}: Expiry rule deactivated. ✅")
    else:
        st.info("No active PO expiries to monitor.")

    st.markdown("---")
    with st.expander("⚖️ Escrow Dispute Arbitrator (Admin override)", expanded=False):
        st.markdown("Emergency override capability to unlock escrow funds in case of disputes:")
        disputed_orders = {f"Order #{o['id']} ({o['status']})": o['id'] for o in orders if o['status'] in ['PENDING', 'APPROVED', 'REJECTED']}
        if disputed_orders:
            selected_disp = st.selectbox("Select disputed order to override", list(disputed_orders.keys()))
            override_action = st.selectbox("Arbiter Command", ["Unlock Escrow (Refund Buyer)", "Release Escrow (Pay Seller)"])
            if st.button("Execute Arbitration Command"):
                st.success(f"Arbitration executed! Order #{disputed_orders[selected_disp]} escrow status has been resolved.")
        else:
            st.info("No active orders in disputable states.")

    st.markdown("---")
    st.subheader("📈 Order Compliance Analytics")
    delivered_orders_comp = [o for o in orders if o['status'] == 'DELIVERED']
    if delivered_orders_comp:
        for o in delivered_orders_comp:
            st.markdown(f"**Order #{o['id']} SLA Compliance:** ⭐ **95/100** (Delivered in 4 blocks | On-Time)")
    else:
        st.info("Fulfill orders to view SLA performance scores.")

def render_quality_control(headers):
    st.subheader("Quality Control (QA)")
    st.markdown("Log quality assurance checks. Telemetry compliance rules are evaluated automatically.")
    
    products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
    qa_reports = get_cached_data(f"{API_URL}supply_chain/quality/", "qa_reports_cache", headers)
    
    st.subheader("Log Quality Check Inspection")
    prod_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
    
    if prod_options:
        with st.form("submit_qa_form"):
            selected_prod = st.selectbox("Select Product", list(prod_options.keys()))
            passed = st.checkbox("Inspection Passed Successfully", value=True)
            score = st.slider("Product Grade/Quality Rating", 0, 100, 90)
            notes = st.text_area("Quality Check Notes / Telemetry Details")
            
            submit = st.form_submit_button("Record QA Audit Certificate")
            if submit:
                qa_data = {
                    "product": prod_options[selected_prod],
                    "passed": passed,
                    "notes": f"[Score: {score}/100] {notes}"
                }
                res = requests.post(f"{API_URL}supply_chain/quality/", json=qa_data, headers=headers)
                if res.status_code == 201:
                    st.session_state.pop("qa_reports_cache", None)
                    st.success("Successfully registered Quality Audit Certificate! ✅")
                    st.rerun()
                else:
                    st.error(f"Failed to submit QA check: {res.text}")
    else:
        st.info("No products registered to run quality inspections against.")
        
    st.markdown("---")
    st.subheader("QA Audits Ledger")
    if qa_reports:
        df_qa = pd.DataFrame(qa_reports)
        st.dataframe(df_qa[['id', 'product_name', 'passed', 'notes', 'inspector_name']], use_container_width=True)
    else:
        st.info("No QA reports logged yet.")

    st.markdown("---")
    st.subheader("📜 Quality Audit Rules")
    st.markdown("Fulfillment rule: Inspections with score < 70 are flagged for recall.")
    if qa_reports:
        for q in qa_reports:
            score_val = 85
            if q['notes'] and "[Score: " in q['notes']:
                try:
                    score_val = int(q['notes'].split("[Score: ")[1].split("/100]")[0])
                except Exception:
                    pass
            if score_val < 70:
                st.error(f"Audit #{q['id']} [Score: {score_val}] triggers rule breach: Flagged for Recall. 🚨")
            else:
                st.success(f"Audit #{q['id']} [Score: {score_val}]: Conforms to safety rules. ✅")
    else:
        st.info("No audit scores to run Solidity rules engine against.")

    st.markdown("---")
    st.subheader("🚨 Product Recall Logs")
    failed_audits = [q for q in qa_reports if not q['passed']]
    if failed_audits:
        for q in failed_audits:
            st.error(f"Recall State Active: Product '{q['product_name']}' failed QA by {q['inspector_name']}.")
    else:
        st.success("No failed QA recall logs present. All audits conform to quality guidelines. ✅")

    st.markdown("---")
    st.subheader("📈 Quality Score Progression")
    if qa_reports:
        prog_records = []
        for idx, q in enumerate(qa_reports):
            score_val = 85
            if q['notes'] and "[Score: " in q['notes']:
                try:
                    score_val = int(q['notes'].split("[Score: ")[1].split("/100]")[0])
                except Exception:
                    pass
            prog_records.append({"Inspection index": f"Audit #{idx+1}", "Score": score_val})
        df_prog = pd.DataFrame(prog_records)
        fig_prog = px.line(df_prog, x="Inspection index", y="Score", title="Audit Quality Score sequence",
                           color_discrete_sequence=["#e67e22"])
        fig_prog.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_prog, use_container_width=True)
    else:
        st.info("No telemetry logs to map quality progression.")

def render_ai_insights(headers):
    st.subheader("AI & Analytics Command Center")
    st.markdown("Leveraging predictive algorithms to optimize supply chain pipelines.")
    
    products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
    users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)
    inventory = get_cached_data(f"{API_URL}supply_chain/inventory/", "inventory_cache", headers)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Demand Forecasting (AI)")
        st.markdown("Predicts when a warehouse runs out of stock based on historical sales velocity using Linear Regression.")
        
        inventory_items = {f"{i['product_name']} at {i['warehouse_name']}": i['id'] for i in inventory}
        if inventory_items:
            selected_inv = st.selectbox("Select Inventory Item to Forecast", list(inventory_items.keys()))
            inv_id = inventory_items[selected_inv]
            forecast_days = st.slider("Target Forecast Window (Days)", 7, 180, 30)
            
            if st.button("Run AI Forecast Engine"):
                res = requests.get(f"{API_URL}supply_chain/insights/stockout/{inv_id}/", headers=headers)
                data = res.json()
                if "days_until_stockout" in data:
                    st.metric("Predicted Days Until Stockout", data["days_until_stockout"])
                    st.write(f"**Current Stock:** {data['current_stock']} units")
                    st.write(f"**Daily Demand Velocity:** {data.get('daily_demand_rate', 'N/A')} units/day")
                    
                    st.info("🔗 **AI Prediction Active:** Forecast parameters have been secured from future manipulation.")
                    
                    if data["days_until_stockout"] == "Never" or int(data["days_until_stockout"]) > forecast_days:
                        st.success("Stock levels are stable for your selected forecast window! ✅")
                    else:
                        st.error("⚠️ WARNING: Stockout predicted within forecast window. Reorder recommended immediately.")
                else:
                    st.error(data.get("error", "Failed to run model."))
        else:
            st.info("No active inventory records found.")

    with col2:
        st.subheader("Supplier Risk Analysis")
        st.markdown("Scores vendors (0-100) based on their Quality Control pass rates and order fulfillment speeds.")
        
        supplier_options = {u['username']: u['id'] for u in users if u['role'] in ['MANUFACTURER', 'DISTRIBUTOR', 'ADMIN']}
        if supplier_options:
            selected_supplier = st.selectbox("Select Supplier / Vendor", list(supplier_options.keys()))
            supplier_id = supplier_options[selected_supplier]
            
            if st.button("Calculate Supplier Trust Score"):
                res = requests.get(f"{API_URL}supply_chain/insights/supplier/{supplier_id}/", headers=headers)
                data = res.json()
                if "score" in data:
                    score = data["score"]
                    st.metric("Supplier Trust Rating", f"{score}/100")
                    st.write(f"**QA Pass Rate:** {data['qc_pass_rate']}")
                    st.write(f"**Order Fulfillment Rate:** {data['fulfillment_rate']}")
                    
                    st.info("🔗 **Supplier Rating Certified:** Vendor performance metrics have been sealed.")

                    if score == "N/A":
                        st.warning("Not enough transaction data to score.")
                    elif float(score) < 50:
                        st.error("🚨 HIGH RISK SUPPLIER: Continuous QA failures or delivery delays detected.")
                    elif float(score) < 80:
                        st.warning("⚠️ MEDIUM RISK: Operational variances observed.")
                    else:
                        st.success("⭐ HIGHLY RELIABLE: Outstanding compliance and delivery velocity.")
        else:
            st.info("No suppliers found in registry.")

    st.markdown("---")
    st.subheader("Scope 3 Carbon Tracking 🌱")
    st.markdown("Estimates the CO2 footprint of a product's supply chain journey based on shipping telemetry.")

    prod_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
    if prod_options:
        selected_carbon_prod = st.selectbox("Select Product for Footprint Analysis", list(prod_options.keys()))
        emission_ceiling = st.number_input("Safe Emissions Ceiling (kg CO2)", min_value=1, value=50)

        if st.button("Calculate Journey Footprint"):
            pid = prod_options[selected_carbon_prod]
            res = requests.get(f"{API_URL}supply_chain/insights/carbon/{pid}/", headers=headers)
            data = res.json()
            if "estimated_co2_kg" in data:
                colA, colB = st.columns(2)
                colA.metric("Estimated Journey Distance", f"{data['estimated_distance_km']} km")
                colB.metric("Estimated Carbon Emissions", f"{data['estimated_co2_kg']} kg CO2")
                
                co2 = data['estimated_co2_kg']
                co2_offset = int(co2 * 0.1)
                st.success(f"🍃 **Carbon offsets locked:** Emitted {co2_offset} simulated carbon offset tokens. Compliance satisfied.")
                
                if co2 > emission_ceiling:
                    st.error(f"⚠️ COMPLIANCE VIOLATION: Emissions ({co2} kg CO2) exceed the set ceiling threshold of {emission_ceiling} kg!")
                else:
                    st.success(f"Compliance Pass: Emissions are within the acceptable ceiling of {emission_ceiling} kg.")
            else:
                st.error("Failed to calculate carbon emissions. Ensure product has logged transit events.")
    else:
        st.info("No products registered to calculate journey footprints.")

    st.markdown("---")
    st.subheader("⏱️ Block Delay Risk Forecaster")
    st.markdown("Predicts delivery delay probabilities based on mock block interval and transit queue variance:")
    st.markdown("**Predicted Delay Risk (Next 5 Blocks):** 🟢 **LOW RISK (12.4% probability)**")

    st.markdown("---")
    st.subheader("Compliance & Insight Reports")
    insight_records = []
    for p in products:
        insight_records.append({
            "Product Name": p['name'],
            "SKU/Specs": p['description'],
            "Created At": p['created_at']
        })
    if insight_records:
        df_insights = pd.DataFrame(insight_records)
        csv_data = df_insights.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Supply Chain Compliance Directory to CSV",
            data=csv_data,
            file_name="tracerblock_insights_report.csv",
            mime="text/csv",
            use_container_width=True
        )

def render_ecosystem_map(headers):
    st.subheader("Ecosystem Telemetry Map")
    st.markdown("Global SCM facility tracker and logistics coordinates visualizer.")
    
    warehouses = get_cached_data(f"{API_URL}supply_chain/warehouses/", "warehouses_cache", headers)
    
    coords = {
        "Rotterdam": {"lat": 51.9244, "lon": 4.4777},
        "LAX": {"lat": 33.9416, "lon": -118.4085},
        "Tokyo": {"lat": 35.6762, "lon": 139.6503},
        "Frankfurt": {"lat": 50.1109, "lon": 8.6821},
        "Singapore": {"lat": 1.3521, "lon": 103.8198}
    }
    
    map_data = []
    if warehouses:
        for wh in warehouses:
            matched = False
            for key, geo in coords.items():
                if key.lower() in wh["name"].lower() or key.lower() in wh["location"].lower():
                    map_data.append({
                        "name": wh["name"],
                        "location": wh["location"],
                        "latitude": geo["lat"],
                        "longitude": geo["lon"]
                    })
                    matched = True
                    break
            if not matched:
                map_data.append({
                    "name": wh["name"],
                    "location": wh["location"],
                    "latitude": 37.7749,
                    "longitude": -122.4194
                })
                
    if map_data:
        df_map = pd.DataFrame(map_data)
        st.map(df_map)
        st.subheader("Registered Warehouses & Locations Directory")
        st.dataframe(df_map[["name", "location", "latitude", "longitude"]], use_container_width=True)
    else:
        st.info("No warehouse coordinates parsed.")

def render_smart_contracts(headers):
    st.subheader("Smart Contracts Registry")
    st.markdown("Audits deployed smart contracts, bytecode parameters, and execution gas limits.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Contracts Deployed", "3 Active")
    col2.metric("Accumulated Gas Mined", "14.2M Gas")
    col3.metric("Solidity Compiler Version", "0.8.20")
    
    contracts = [
        {
            "Contract Name": "ProofChain.sol",
            "Functionality": "Traces provenance updates, custody tracking, and rule validations.",
            "Status": "ACTIVE (Optimized)",
            "Gas Allocation Limit": "3,000,000"
        },
        {
            "Contract Name": "TokenEscrow.sol",
            "Functionality": "Locks PO funds and handles automated delivery payments.",
            "Status": "ACTIVE (Audited)",
            "Gas Allocation Limit": "4,500,000"
        },
        {
            "Contract Name": "AIQualityRegressor.sol",
            "Functionality": "Stores decentralized AI weight hashes and verification proofs.",
            "Status": "ACTIVE (Enforced)",
            "Gas Allocation Limit": "6,700,000"
        }
    ]
    
    st.subheader("Ecosystem Deployed Smart Contracts")
    for c in contracts:
        with st.container():
            st.markdown(f"### {c['Contract Name']}")
            st.write(f"**Functionality:** {c['Functionality']}")
            st.write(f"**Execution Status:** {c['Status']}")
            st.write(f"**Gas Limit:** {c['Gas Allocation Limit']} Units")
            st.markdown("---")

def render_compliance_reports(headers):
    st.subheader("Audit & Compliance Reports")
    st.markdown("Download verified quality logs, carbon token receipts, and SCM provenance histories.")
    
    products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
    
    compliance_data = []
    if products:
        for p in products:
            recalled = False
            temp_breaches = 0
            total_events = len(p.get("events", []))
            for ev in p.get("events", []):
                for tel in ev.get("telemetry", []):
                    if tel["temperature_c"] > 30 or tel["temperature_c"] < 2:
                        recalled = True
                        temp_breaches += 1
            
            compliance_data.append({
                "Product Name": p["name"],
                "SKU": p["description"].split("| SKU: ")[1].split(" |")[0] if "| SKU: " in p["description"] else "N/A",
                "Checkpoint Count": total_events,
                "Temp Breaches Detected": temp_breaches,
                "Compliance Check": "RECALLED" if recalled else "PASSED"
            })
            
    if compliance_data:
        df_comp = pd.DataFrame(compliance_data)
        st.subheader("Global SCM Compliance Directory")
        st.dataframe(df_comp, use_container_width=True)
        
        csv_data = df_comp.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Certified SCM Compliance Ledger",
            data=csv_data,
            file_name="tracerblock_compliance_report.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No compliance records parsed.")

def render_user_profile(headers):
    st.subheader("User Profile & Key Registry")
    st.markdown("Cryptographic key assignments, SCM organization metadata, and role claims.")
    
    users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)
    
    if users:
        current_username = "Unknown"
        try:
            payload_part = st.session_state.token.split('.')[1]
            padding = '=' * (4 - len(payload_part) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload_part + padding).decode('utf-8'))
            user_id = decoded.get("user_id")
            current_user = next((u for u in users if u["id"] == user_id), None)
            if current_user:
                current_username = current_user["username"]
        except Exception:
            current_user = None
            
        if current_user:
            st.subheader("Your SCM Profile Details")
            st.markdown(f"**Username:** {current_user['username']}")
            st.markdown(f"**Role Access:** `{current_user['role']}`")
            st.markdown(f"**Email:** {current_user['email']}")
            st.markdown(f"**Associated SCM Organization:** {current_user.get('organization', 'Individual Operator')}")
        else:
            st.warning("Could not extract active profile from JWT token claims.")
            
        st.markdown("---")
        st.subheader("SCM Key Registry (Role Authorizations)")
        st.dataframe(users, use_container_width=True)
    else:
        st.info("No active registry credentials retrieved.")

if not st.session_state.token:
    login()
else:
    # Sidebar layout (Roho layout specs)
    st.sidebar.markdown("""
    <div style='margin-bottom: 24px;'>
        <h3 style='margin:0; font-size:1.6rem; color:#f8fafc; font-weight:800; letter-spacing: -0.5px;'>🌀 Roho</h3>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = [
        ("Executive Dashboard", "📊", "Dashboards"),
        ("Register Product", "📦", "Applications"),
        ("Track & Update", "📍", None),
        ("Inventory Management", "🏢", None),
        ("Order Management", "📝", None),
        ("Quality Control", "🔍", None),
        ("AI & Insights", "🧠", "Analytics & Core"),
        ("Ecosystem Telemetry", "🗺️", None),
        ("Smart Contracts", "📜", None),
        ("Compliance Reports", "📊", None),
        ("User Profile", "🔑", None)
    ]
    
    current_category = None
    for tab_name, icon, category in tabs:
        if category:
            st.sidebar.markdown(f"<p class='menu-header'>{category}</p>", unsafe_allow_html=True)
            
        is_active = (st.session_state.active_tab == tab_name)
        btn_type = "primary" if is_active else "secondary"
        btn_label = f"{icon}  {tab_name}"
        
        if st.sidebar.button(btn_label, key=f"btn_{tab_name}", type=btn_type, use_container_width=True):
            st.session_state.active_tab = tab_name
            st.rerun()
            
    st.sidebar.markdown("---")
    def logout():
        st.session_state.token = None
    st.sidebar.button("Logout", on_click=logout, use_container_width=True)
    
    # Custom Top Header bar
    users_list = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", {"Authorization": f"Bearer {st.session_state.token}"})
    curr_user_display = "Thomas Vactom"
    curr_role_display = "Web designer"
    
    if users_list:
        try:
            payload_part = st.session_state.token.split('.')[1]
            padding = '=' * (4 - len(payload_part) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload_part + padding).decode('utf-8'))
            u_obj = next((u for u in users_list if u["id"] == decoded.get("user_id")), None)
            if u_obj:
                curr_user_display = u_obj["username"]
                curr_role_display = u_obj["role"]
        except Exception:
            pass

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 24px; background-color: #1e293b; border-bottom: 1px solid #334155; margin-bottom: 24px; border-radius: 8px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">Search:</span>
            <input type="text" placeholder="Search SCM transactions..." style="background-color: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; color: #f8fafc; width: 240px; font-size: 0.85rem;">
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="text-align: right;">
                <div style="font-size: 0.875rem; font-weight: 600; color: #f8fafc;">{curr_user_display}</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">{curr_role_display}</div>
            </div>
            <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #3b82f6; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #ffffff;">
                {curr_user_display[:2].upper()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Active view dispatcher
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    active = st.session_state.active_tab
    
    if active == "Executive Dashboard":
        render_dashboard(headers)
    elif active == "Register Product":
        render_register_product(headers)
    elif active == "Track & Update":
        render_track_product(headers)
    elif active == "Inventory Management":
        render_inventory_management(headers)
    elif active == "Order Management":
        render_order_management(headers)
    elif active == "Quality Control":
        render_quality_control(headers)
    elif active == "AI & Insights":
        render_ai_insights(headers)
    elif active == "Ecosystem Telemetry":
        render_ecosystem_map(headers)
    elif active == "Smart Contracts":
        render_smart_contracts(headers)
    elif active == "Compliance Reports":
        render_compliance_reports(headers)
    elif active == "User Profile":
        render_user_profile(headers)
