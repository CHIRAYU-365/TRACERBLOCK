import streamlit as st
import requests
try:
    from frontend.ui_components import load_custom_css
except ModuleNotFoundError:
    from ui_components import load_custom_css
load_custom_css()

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000/api/")

if "token" not in st.session_state or not st.session_state.token:
    st.warning("Please login from the main page first.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("Quality Control (QA) 🔍")

st.markdown("Log quality assurance checks. If an item fails QA or its telemetry data shows safe bounds were exceeded, the Smart Contract will flag it for recall.")

with st.form("qa_form"):
    prod_id = st.number_input("Product ID", min_value=1, step=1)
    inspector_id = st.number_input("Inspector (User ID)", min_value=1, step=1)
    passed = st.checkbox("Passed QA Inspection?", value=True)
    notes = st.text_area("Inspection Notes")
    
    submit_qa = st.form_submit_button("Submit QA Report")
    if submit_qa:
        data = {
            "product": prod_id,
            "inspector": inspector_id,
            "passed": passed,
            "notes": notes
        }
        res = requests.post(f"{API_URL}supply_chain/quality/", json=data, headers=headers)
        if res.status_code == 201:
            st.success("QA Report submitted successfully.")
            if not passed:
                st.warning("Alert: Smart Contract has flagged this product for RECALL.")
        else:
            st.error("Failed to submit QA Report. Ensure Product and Inspector IDs exist.")

st.markdown("---")
st.subheader("Recent QA Reports")
qa_res = requests.get(f"{API_URL}supply_chain/quality/", headers=headers)
if qa_res.status_code == 200:
    st.dataframe(qa_res.json(), use_container_width=True)
