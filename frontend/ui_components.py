import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
    /* Floating Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(30, 30, 47, 0.8) 0%, rgba(42, 42, 64, 0.8) 100%) !important;
        margin: 20px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6) !important;
        height: calc(100vh - 40px) !important;
        border: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
    }
    
    /* Hide the ugly collapse arrow so it looks cleaner */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    
    /* Main App Background */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #0f0f1a) !important;
        color: #e0e0e0;
    }
    
    /* Hide top header */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Input Fields styling */
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
    }

    /* Beautiful Buttons */
    button[kind="secondary"], button[kind="primary"] {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%) !important;
        color: #121212 !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 1rem !important;
    }
    
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0, 242, 254, 0.5) !important;
        color: white !important;
    }
    
    /* Metrics Box gradients */
    div[data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Titles and Headers */
    h1, h2, h3 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Dataframes / Tables */
    [data-testid="stDataFrame"] {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)
