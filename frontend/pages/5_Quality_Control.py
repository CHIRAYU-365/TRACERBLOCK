import streamlit as st
import requests
import plotly.express as px
import pandas as pd
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

st.title("Quality Control (QA) 🔍")
st.markdown("Log quality assurance checks. If an item fails QA or its telemetry data shows safe bounds were exceeded, the Smart Contract will flag it for recall.")

products = get_cached_data(f"{API_URL}supply_chain/products/", "products_cache", headers)
users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)
qa_reports = get_cached_data(f"{API_URL}supply_chain/quality/", "qa_reports_cache", headers)

if qa_reports:
    total_checks = len(qa_reports)
    passed_checks = sum(1 for q in qa_reports if q['passed'])
    pass_rate = (passed_checks / total_checks) * 100
    failed_checks = total_checks - passed_checks
else:
    total_checks, pass_rate, failed_checks = 0, 100.0, 0

mcol1, mcol2, mcol3 = st.columns(3)
mcol1.metric("Total Quality Audits", total_checks)
mcol2.metric("Average Pass Rate", f"{pass_rate:.1f}%")
mcol3.metric("Failed / Recalled Batches", failed_checks)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Log Quality Audit Checkpoint")
    with st.form("qa_form"):
        prod_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
        selected_prod = st.selectbox("Select Audited Product", list(prod_options.keys()))
        
        inspector_options = {u['username']: u['id'] for u in users if u['role'] in ['QA', 'ADMIN']}
        selected_inspector = st.selectbox("Assigned Auditor", list(inspector_options.keys()))
        
        passed = st.checkbox("Verify: Product Meets QA Standards?", value=True)
        score = st.slider("Inspection Score (0-100)", 0, 100, 85)
        notes = st.text_area("Audit Findings & Action Notes", placeholder="Enter notes...")
        
        submit_qa = st.form_submit_button("Submit QA Audit Certificate")
        if submit_qa:
            if not selected_prod or not selected_inspector:
                st.error("Please select both product and inspector.")
            else:
                combined_notes = f"[Score: {score}/100] {notes}"
                qa_data = {
                    "product": prod_options[selected_prod],
                    "inspector": inspector_options[selected_inspector],
                    "passed": passed,
                    "notes": combined_notes
                }
                res = requests.post(f"{API_URL}supply_chain/quality/", json=qa_data, headers=headers)
                if res.status_code == 201:
                    st.session_state.pop("qa_reports_cache", None)
                    st.success("QA Report submitted successfully! ✅")
                    if not passed:
                        st.warning("ALERT: Contract recalled status has been triggered.")
                    st.rerun()
                else:
                    st.error(f"Failed to submit QA report: {res.text}")

with col2:
    st.subheader("QA Inspection Compliance")
    if qa_reports:
        df_qa = pd.DataFrame(qa_reports)
        pass_fail_counts = df_qa['passed'].value_counts().reset_index()
        pass_fail_counts.columns = ['Status', 'Count']
        pass_fail_counts['Status'] = pass_fail_counts['Status'].map({True: 'Passed', False: 'Failed/Recalled'})
        
        fig = px.pie(pass_fail_counts, names='Status', values='Count', 
                     title="Compliance Pass vs Fail Audit Distribution",
                     color_discrete_sequence=["#2ecc71", "#e74c3c"])
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No compliance data to map yet.")

st.markdown("---")
st.subheader("Interactive Quality Assurance Ledger")

filter_passed = st.selectbox("Filter Ledger display status", ["All", "Passed Audits", "Failed/Recalled Audits"])

if qa_reports:
    df_ledger = pd.DataFrame(qa_reports)
    if filter_passed == "Passed Audits":
        df_ledger = df_ledger[df_ledger['passed'] == True]
    elif filter_passed == "Failed/Recalled Audits":
        df_ledger = df_ledger[df_ledger['passed'] == False]
        
    if not df_ledger.empty:
        st.dataframe(df_ledger[['id', 'product_name', 'inspector_name', 'passed', 'notes', 'timestamp']], width="stretch")
        
        csv_data = df_ledger.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export QA Audit Ledger to CSV",
            data=csv_data,
            file_name="tracerblock_quality_audits.csv",
            mime="text/csv"
        )
    else:
        st.info("No logs match the selected filter.")
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
