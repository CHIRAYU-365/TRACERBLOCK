import streamlit as st
import requests

def get_cached_data(url, cache_key, headers):
    if cache_key not in st.session_state or st.session_state[cache_key] is None:
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                st.session_state[cache_key] = res.json()
            else:
                st.session_state[cache_key] = []
        except Exception:
            st.session_state[cache_key] = []
    return st.session_state[cache_key]

def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Outfit', sans-serif !important;
        background-color: #030305 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.08) 0, transparent 50%),
            radial-gradient(at 50% 0%, rgba(236, 72, 153, 0.06) 0, transparent 50%),
            radial-gradient(at 100% 0%, rgba(6, 180, 212, 0.08) 0, transparent 50%) !important;
        background-attachment: fixed !important;
        color: #f3f4f6 !important;
    }
    
    code, pre, stCodeBlock, .stCodeBlock code {
        font-family: 'JetBrains Mono', monospace !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 15, 0.7) !important;
        margin: 16px !important;
        border-radius: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
        height: calc(100vh - 32px) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
    }
    
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        color: #ffffff !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border-color: rgba(236, 72, 153, 0.6) !important;
        box-shadow: 0 0 16px rgba(236, 72, 153, 0.25) !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
    }

    button[kind="secondary"], button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0.6rem 1.6rem !important;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.25) !important;
    }
    
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(236, 72, 153, 0.45) !important;
    }
    
    button[kind="secondary"]:active, button[kind="primary"]:active {
        transform: translateY(0) !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(18, 18, 28, 0.65) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        border-radius: 24px !important;
        padding: 24px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(236, 72, 153, 0.4) !important;
        box-shadow: 0 16px 40px rgba(236, 72, 153, 0.2) !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #a78bfa, #f472b6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #ffffff, #9ca3af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .streamlit-expanderHeader {
        background-color: rgba(18, 18, 28, 0.4) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: rgba(18, 18, 28, 0.6) !important;
        border-color: rgba(236, 72, 153, 0.3) !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 20px !important;
        overflow: hidden !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.5) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        background: rgba(10, 10, 15, 0.4) !important;
    }
    
    .blockchain-indicator {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 30px !important;
        padding: 6px 16px !important;
        color: #a78bfa !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.85em !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.15) !important;
        display: inline-block !important;
        margin-bottom: 12px !important;
    }
    
    .solidity-badge {
        background: linear-gradient(135deg, rgba(230, 126, 34, 0.12) 0%, rgba(241, 196, 15, 0.12) 100%) !important;
        border: 1px solid rgba(230, 126, 34, 0.25) !important;
        border-radius: 30px !important;
        padding: 6px 16px !important;
        color: #f97316 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.85em !important;
        display: inline-block !important;
        margin-bottom: 12px !important;
    }
    
    .verified-badge {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        border-radius: 30px !important;
        padding: 6px 16px !important;
        color: #10b981 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.85em !important;
        display: inline-block !important;
    }

    .login-mask {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(circle at 50% 50%, #0a0a14 0%, #020205 100%) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        z-index: 999990 !important;
    }
    
    .login-popup {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 440px;
        background: rgba(12, 12, 20, 0.85) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 24px 80px rgba(139, 92, 246, 0.22) !important;
        backdrop-filter: blur(40px) !important;
        -webkit-backdrop-filter: blur(40px) !important;
        z-index: 999999 !important;
    }

    @keyframes pageFadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    [data-testid="stAppViewContainer"] {
        animation: pageFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    </style>
    """, unsafe_allow_html=True)
