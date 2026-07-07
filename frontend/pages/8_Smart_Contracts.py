import streamlit as st
import os

try:
    from frontend.ui_components import load_custom_css
except ModuleNotFoundError:
    from ui_components import load_custom_css
load_custom_css()

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

st.title("Smart Contracts Registry 📜")
st.markdown("Audits deployed smart contracts, verified bytecode compilations, and transaction gas parameters.")

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

st.subheader("Ecosystem Smart Contracts Directory")
for c in contracts:
    with st.container():
        st.markdown(f"### {c['Contract Name']}")
        st.write(f"**Description:** {c['Functionality']}")
        st.write(f"**Execution Status:** {c['Status']}")
        st.write(f"**Gas Limit:** {c['Gas Allocation Limit']} Units")
        st.markdown("---")
