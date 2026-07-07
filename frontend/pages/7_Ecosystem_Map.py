import streamlit as st
import pandas as pd
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

st.title("Ecosystem Telemetry Map 🗺️")
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
