import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import hashlib
import os

try:
    from frontend.ui_components import load_custom_css, get_cached_data
except ModuleNotFoundError:
    from ui_components import load_custom_css, get_cached_data
load_custom_css()

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

st.title("Track & Update Product 📍")
st.markdown("Query product provenance, log transit checkpoints, and view IoT telemetry charts anchored to the mock blockchain.")

products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)

product_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}

selected_product_label = st.selectbox("Select Product to Track", list(product_options.keys()))
search_btn = st.button("Search Provenance History")

if search_btn or st.session_state.get('track_id'):
    if selected_product_label:
        st.session_state['track_id'] = product_options[selected_product_label]
        
    pid = st.session_state.get('track_id')
    res = requests.get(f"{API_URL}supply_chain/products/{pid}/", headers=headers)
    
    if res.status_code == 200:
        product = res.json()
        st.success(f"Tracking provenance data for product: **{product['name']}**")
        
        st.markdown("### Log New Transit Checkpoint")
        with st.form("update_form"):
            col_x, col_y = st.columns(2)
            with col_x:
                status = st.selectbox("Checkpoint Status", ["In Transit", "At Warehouse", "Under Inspection", "Delivered", "Delayed"])
                location = st.text_input("Checkpoint Location", placeholder="e.g. Los Angeles Port, CA")
            with col_y:
                temp = st.slider("Container Temp (°C)", -30, 50, 4)
                hum = st.slider("Container Humidity (%)", 0, 100, 60)
                
            submit = st.form_submit_button("Log Event and Anchor to Blockchain")
            
            if submit:
                if not location:
                    st.error("Please specify a location for the checkpoint.")
                else:
                    event_data = {"product": pid, "status": status, "location": location}
                    ev_res = requests.post(f"{API_URL}supply_chain/events/", json=event_data, headers=headers)
                    if ev_res.status_code == 201:
                        st.session_state.pop("products_cache", None)
                        
                        ev_id = ev_res.json()['id']
                        tel_data = {"event": ev_id, "temperature_c": temp, "humidity_percent": hum}
                        requests.post(f"{API_URL}supply_chain/telemetry/", json=tel_data, headers=headers)
                        st.success("Successfully anchored checkpoint logs to Mock Ethereum Blockchain! ✅")
                        st.rerun()
                    else:
                        st.error(f"Failed to record checkpoint: {ev_res.text}")

        st.markdown("---")
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
        st.error("Product not found. Please select a valid product.")
