import streamlit as st
import requests

def get_cached_data(url, cache_key, headers):
    if cache_key not in st.session_state or st.session_state[cache_key] is None:
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                st.session_state[cache_key] = res.json()
            elif res.status_code in [401, 403]:
                st.session_state.token = None
                st.session_state.pop(cache_key, None)
                st.rerun()
            else:
                st.session_state[cache_key] = []
        except Exception:
            st.session_state[cache_key] = []
    return st.session_state[cache_key]

def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    
    code, pre, stCodeBlock, .stCodeBlock code {
        font-family: 'JetBrains Mono', monospace !important;
    }

    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        margin: 0px !important;
        border-radius: 0px !important;
        height: 100vh !important;
        border-right: 1px solid #334155 !important;
    }
    
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: 1px solid #334155 !important;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        color: #f8fafc !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25) !important;
    }

    button[kind="secondary"], button[kind="primary"] {
        background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2) !important;
    }
    
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        opacity: 0.95 !important;
        box-shadow: 0 6px 8px -1px rgba(59, 130, 246, 0.3) !important;
    }
    
    button[kind="secondary"]:active, button[kind="primary"]:active {
        transform: translateY(0) !important;
    }

    div[data-testid="stMetric"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
        background: none !important;
        -webkit-text-fill-color: #f8fafc !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    h1 {
        font-size: 2.25rem !important;
        -webkit-text-fill-color: #f8fafc !important;
    }

    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid #334155 !important;
        background: #1e293b !important;
    }
    
    .blockchain-indicator {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 20px !important;
        padding: 4px 12px !important;
        color: #60a5fa !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600;
        font-size: 0.85em !important;
        display: inline-block !important;
        margin-bottom: 12px !important;
    }
    
    .solidity-badge {
        background: rgba(249, 115, 22, 0.1) !important;
        border: 1px solid rgba(249, 115, 22, 0.3) !important;
        border-radius: 20px !important;
        padding: 4px 12px !important;
        color: #fb923c !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600;
        font-size: 0.85em !important;
        display: inline-block !important;
        margin-bottom: 12px !important;
    }
    
    .verified-badge {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 20px !important;
        padding: 4px 12px !important;
        color: #34d399 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600;
        font-size: 0.85em !important;
        display: inline-block !important;
    }



    [data-testid="stSidebar"] button[kind="secondary"] {
        background: transparent !important;
        color: #94a3b8 !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
        padding: 10px 16px !important;
        width: 100% !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #f8fafc !important;
    }
    
    [data-testid="stSidebar"] button[kind="primary"] {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #3b82f6 !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
        padding: 10px 16px !important;
        width: 100% !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    .menu-header {
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        margin-top: 18px !important;
        margin-bottom: 6px !important;
        letter-spacing: 0.5px !important;
        padding-left: 12px !important;
    }

    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    @keyframes pageFadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    [data-testid="stAppViewContainer"] {
        animation: pageFadeIn 0.2s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)
