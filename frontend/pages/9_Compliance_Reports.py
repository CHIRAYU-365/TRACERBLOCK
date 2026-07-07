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

st.title("Audit & Compliance Reports 📊")
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
    st.subheader("Global Compliance Directory")
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
