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

    /* Global Body styling & Font override */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Outfit', sans-serif !important;
        background: radial-gradient(circle at 10% 20%, #151528 0%, #080812 90%) !important;
        color: #e2e8f0 !important;
    }
    
    code, pre, stCodeBlock, .stCodeBlock code {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Floating Translucent Glassmorphic Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(18, 18, 35, 0.5) !important;
        margin: 15px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
        height: calc(100vh - 30px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
    }
    
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    
    /* Clean and subtle top header */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Input Field glassmorphism with Focus Glows */
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border-color: rgba(0, 242, 254, 0.5) !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
    }

    /* Styled buttons with glass gradient & micro-animations */
    button[kind="secondary"], button[kind="primary"] {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #0b0b16 !important;
        border-radius: 30px !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2) !important;
    }
    
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 242, 254, 0.45) !important;
        color: #ffffff !important;
    }

    /* Glassmorphic Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(25, 25, 45, 0.4) !important;
        border: 1px solid rgba(0, 242, 254, 0.12) !important;
        border-radius: 18px !important;
        padding: 20px !important;
        backdrop-filter: blur(15px) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(0, 242, 254, 0.35) !important;
        box-shadow: 0 12px 40px 0 rgba(0, 242, 254, 0.18) !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #00f2fe, #a18cd1) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }

    /* Typography & Headers styling */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Expanders & Accordions */
    .streamlit-expanderHeader {
        background-color: rgba(25, 25, 45, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: rgba(25, 25, 45, 0.5) !important;
        border-color: rgba(0, 242, 254, 0.2) !important;
    }

    /* Clean Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        background: rgba(18, 18, 30, 0.4) !important;
    }
    
    /* Custom Blockchain Indicator Badges */
    .blockchain-indicator {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(161, 140, 209, 0.1) 100%) !important;
        border: 1px solid rgba(0, 242, 254, 0.25) !important;
        border-radius: 30px !important;
        padding: 4px 14px !important;
        color: #00f2fe !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.85em !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.1) !important;
        display: inline-block !important;
        margin-bottom: 10px !important;
    }
    
    .solidity-badge {
        background: linear-gradient(135deg, rgba(230, 126, 34, 0.15) 0%, rgba(241, 196, 15, 0.15) 100%) !important;
        border: 1px solid rgba(230, 126, 34, 0.3) !important;
        border-radius: 30px !important;
        padding: 4px 14px !important;
        color: #e67e22 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.85em !important;
        display: inline-block !important;
        margin-bottom: 10px !important;
    }
    
    .verified-badge {
        background: rgba(46, 204, 113, 0.1) !important;
        border: 1px solid rgba(46, 204, 113, 0.3) !important;
        border-radius: 30px !important;
        padding: 4px 14px !important;
        color: #2ecc71 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.85em !important;
        display: inline-block !important;
    }

    /* Viewport Login Masking & Floating Popup Overlay */
    .login-mask {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(circle at 50% 50%, #0d0d1e 0%, #030308 100%) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        z-index: 999990 !important;
    }
    
    .login-popup {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 440px;
        background: rgba(18, 18, 30, 0.8) !important;
        border: 1px solid rgba(0, 242, 254, 0.25) !important;
        border-radius: 24px !important;
        padding: 40px !important;
        box-shadow: 0 20px 60px rgba(0, 242, 254, 0.18) !important;
        backdrop-filter: blur(40px) !important;
        -webkit-backdrop-filter: blur(40px) !important;
        z-index: 999999 !important;
    }
    </style>
    """, unsafe_allow_html=True)
