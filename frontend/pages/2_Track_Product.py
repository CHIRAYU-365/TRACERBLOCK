import streamlit as st
import requests
from frontend.ui_components import load_custom_css
load_custom_css()
import pandas as pd
import plotly.express as px

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000/api/")

if "token" not in st.session_state or not st.session_state.token:
    st.warning("Please login from the main page first.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("Track & Update Product 📍")

product_id = st.number_input("Enter Product ID", min_value=1, step=1)
if st.button("Search"):
    st.session_state['track_id'] = product_id

if st.session_state.get('track_id'):
    pid = st.session_state['track_id']
    res = requests.get(f"{API_URL}supply_chain/products/{pid}/", headers=headers)
    if res.status_code == 200:
        product = res.json()
        st.success(f"Tracking: {product['name']}")
        
        st.markdown("### Update Status & Telemetry")
        with st.form("update_form"):
            status = st.selectbox("Status", ["In Transit", "At Warehouse", "Delivered"])
            location = st.text_input("Location")
            temp = st.slider("Temperature (°C)", -20, 50, 20)
            hum = st.slider("Humidity (%)", 0, 100, 50)
            submit = st.form_submit_button("Log Event on Blockchain")
            
            if submit:
                event_data = {"product": pid, "status": status, "location": location}
                ev_res = requests.post(f"{API_URL}supply_chain/events/", json=event_data, headers=headers)
                if ev_res.status_code == 201:
                    ev_id = ev_res.json()['id']
                    tel_data = {"event": ev_id, "temperature_c": temp, "humidity_percent": hum}
                    requests.post(f"{API_URL}supply_chain/telemetry/", json=tel_data, headers=headers)
                    st.success("Successfully anchored to Ethereum blockchain! ✅")
                    st.rerun()
                else:
                    st.error(f"Failed: {ev_res.text}")
        
        st.markdown("### Telemetry History")
        if product.get('events'):
            tel_records = []
            for ev in product['events']:
                for tel in ev.get('telemetry', []):
                    tel_records.append({
                        "Time": tel['timestamp'],
                        "Temperature": tel['temperature_c'],
                        "Humidity": tel['humidity_percent']
                    })
            if tel_records:
                df_tel = pd.DataFrame(tel_records)
                fig = px.line(df_tel, x="Time", y=["Temperature", "Humidity"], title="IoT Sensor Data During Transit")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No telemetry data yet.")
                
            st.markdown("### Immutable Blockchain Events")
            st.dataframe(product['events'])
    else:
        st.error("Product not found.")
