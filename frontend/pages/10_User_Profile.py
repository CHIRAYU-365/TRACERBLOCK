import streamlit as st
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

st.title("User Profile & Key Registry 🔑")
st.markdown("Cryptographic key assignments, SCM organization metadata, and role claims.")

users = get_cached_data(f"{API_URL}supply_chain/users/", "users_cache", headers)

if users:
    current_username = "Unknown"
    
    import base64
    import json
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
        st.subheader("Your Profile Details")
        st.markdown(f"**Username:** {current_user['username']}")
        st.markdown(f"**Role:** `{current_user['role']}`")
        st.markdown(f"**Email:** {current_user['email']}")
        st.markdown(f"**Associated SCM Organization:** {current_user.get('organization', 'Individual Operator')}")
    else:
        st.warning("Could not extract active profile from JWT token claims.")
        
    st.markdown("---")
    st.subheader("Key Registry (Role Authorizations)")
    st.dataframe(users, use_container_width=True)
else:
    st.info("No active registry credentials retrieved.")
