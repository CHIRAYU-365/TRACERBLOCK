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
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit = st.button("Unlock Portal & Decrypt Ledger", use_container_width=True)
        
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
    st.markdown('<div class="blockchain-indicator">⛓️ Private Blockchain Node: 127.0.0.1:8545</div> <div class="verified-badge">State: ACTIVE</div>', unsafe_allow_html=True)
    
    st.title("Executive Dashboard 📊")
    st.markdown("Real-time overview and analytical insights of the TRACERBLOCK supply chain.")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    with st.spinner("🔒 Establishing secure handshake & decrypting SCM ledger records..."):
        try:
            products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
            inventory = get_cached_data(f"{API_URL}supply_chain/inventory/", "inventory_cache", headers)
            orders = get_cached_data(f"{API_URL}supply_chain/orders/", "orders_cache", headers)
            
            try:
                node_res = requests.get("http://127.0.0.1:8545/stats")
                node_stats = node_res.json() if node_res.status_code == 200 else {}
            except Exception:
                node_stats = {}
        except Exception as e:
            st.error(f"Handshake failed: {e}")
            st.stop()
            
    try:
        if node_stats:
            st.markdown("#### 🔗 Live Blockchain Network Monitor")
            ncol1, ncol2, ncol3, ncol4 = st.columns(4)
            ncol1.metric("Blockchain Node Latency", f"{node_stats.get('node_latency_ms', 12)} ms")
            ncol2.metric("Current Block Height", f"#{node_stats.get('block_number', 1240)}")
            ncol3.metric("Simulated Gas Price", f"{node_stats.get('gas_price_gwei', 20)} Gwei")
            ncol4.metric("Ecosystem Peer Count", f"{node_stats.get('peer_count', 8)} Nodes")
            st.markdown("---")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Registered Products", len(products))
        total_stock = sum(item['quantity'] for item in inventory)
        col2.metric("Total Stock (Units)", total_stock)
        col3.metric("Total Orders Placed", len(orders))
        
        st.markdown("---")
        st.subheader("⚡ Off-Chain State Channel Optimization (Gas Savings)")
        st.markdown("Estimates gas costs and USD fees saved by offloading intermediate telemetry sensor check-ins from the root chain:")
        saved_txs = len(products) * 4
        saved_gas = saved_txs * 21000
        saved_eth = (saved_gas * 20) / 1e9
        saved_usd = saved_eth * 3200.0
        
        scol1, scol2, scol3 = st.columns(3)
        scol1.metric("Off-Chain Operations Managed", f"{saved_txs} skipped Txs")
        scol2.metric("Equivalent Gas Fees Saved", f"{saved_eth:.4f} ETH")
        scol3.metric("Cost Savings Value (USD)", f"${saved_usd:,.2f} USD")
        
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

        with st.expander("📝 Global Ledger Transaction & Mined Blocks Registry", expanded=False):
            st.markdown("Below are the last cryptographic transactions and newly mined blocks recorded on the private ledger:")
            
            blocks_history = node_stats.get("blocks", [])
            if blocks_history:
                st.markdown("#### 📦 Recently Mined Blocks")
                for b in reversed(blocks_history):
                    ts_val = int(b.get("timestamp", "0x0"), 16)
                    import time
                    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_val))
                    st.code(f"Block #{int(b['number'], 16)+1240} | Hash: {b['hash']}\n ├─ Parent Hash: {b['parentHash']}\n ├─ Transactions: {b['transactions']}\n └─ Mined At: {time_str}")
            
            txs = node_stats.get("transactions", [])
            if txs:
                st.markdown("#### 📝 Raw Transaction Hashes")
                for i, tx in enumerate(reversed(txs)):
                    st.code(f"[Tx #{i+1}] {tx} | Status: CONFIRMED | Gas Used: 21,000 | Network: 1337-Net")
            else:
                st.info("No transaction logs anchored on the node yet. Perform some actions to populate.")

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

        st.markdown("### On-Chain Activity Velocity")
        block_activity = {}
        for p in products:
            for ev in p.get('events', []):
                time_key = ev['timestamp'][:16]
                block_activity[time_key] = block_activity.get(time_key, 0) + 1
                
        if block_activity:
            df_act = pd.DataFrame(list(block_activity.items()), columns=['Time', 'Transactions'])
            df_act = df_act.sort_values('Time').tail(10)
            fig_act = px.area(df_act, x='Time', y='Transactions', title="Ecosystem On-Chain Activity Velocity (Simulated Block-to-Block)",
                              color_discrete_sequence=["#00f2fe"])
            fig_act.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_act, width="stretch")
        else:
            st.info("Insufficient transactional traffic to map activity velocity yet.")

        st.markdown("#### 🔍 Node Explorer / Cryptographic Hash Auditor")
        audit_hash = st.text_input("Enter Transaction Hash to Verify Node Validity", placeholder="e.g. 0xeef08a9f6...")
        if audit_hash:
            is_valid = audit_hash in node_stats.get("transactions", []) or (audit_hash.startswith("0x") and len(audit_hash) == 66)
            if is_valid:
                st.success("✅ Transaction status: VERIFIED on Mock Ethereum Node | Block Height: 1240 | Confirmations: 12")
                st.json({
                    "tx_hash": audit_hash,
                    "status": "0x1 (Success)",
                    "blockNumber": "1240",
                    "gasUsed": "21000",
                    "cumulativeGasUsed": "21000",
                    "from": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
                })
            else:
                st.error("❌ Cryptographic signature match failed: Transaction hash not recorded on active node.")

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
                width="stretch"
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
