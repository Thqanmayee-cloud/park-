import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- 1. CONFIGURATION & PRESTIGE LOOK UI MATRIX ---
st.set_page_config(
    page_title="Park+ Elite Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Complete UI overhaul: Custom fonts, card drop-shadows, and rich color spacing
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Elements */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0B0D12 !important;
        font-family: 'Inter', sans-serif !important;
        color: #F8FAFC !important;
    }
    
    /* Luxury Header Fonts */
    h1, h2, h3, .brand-title {
        font-family: 'Cabinet Grotesk', 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Clean Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #111522 !important;
        border-right: 1px solid #1E2538;
    }
    
    /* Premium Content Cards */
    div.premium-card {
        background: #121724;
        border: 1px solid #1E263C;
        padding: 26px;
        border-radius: 16px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
        margin-bottom: 25px;
    }
    
    /* Custom KPI Stat Boxes */
    div.stat-box {
        background: linear-gradient(145deg, #161D2F 0%, #111624 100%);
        border: 1px solid #222C46;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Vibrant Presentation Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 20px rgba(225, 29, 72, 0.35);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(225, 29, 72, 0.55);
    }
    
    /* Text Inputs and Selection Menus */
    input, select, .stSelectbox, div[data-baseweb="select"] {
        background-color: #161D2F !important;
        color: #FFFFFF !important;
        border: 1px solid #222C46 !important;
        border-radius: 8px !important;
    }
    
    /* Form Labels styling */
    label {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px !important;
    }
    
    /* Progress Bar Overrides */
    div[data-testid="stProgress"] > div > div {
        background-color: #E11D48 !important;
    }
    
    /* Clean Streamlit System Filters */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. DYNAMIC SYSTEM TELEMETRY STATE ---
if 'reservations' not in st.session_state:
    st.session_state.reservations = pd.DataFrame(columns=['Vehicle Plate', 'Profile Type', 'Assigned Lot', 'Timestamp', 'Status'])

# Operational Constraints
TOTAL_CAPACITIES = {"Zone A (Faculty Only)": 50, "Zone B (General Student)": 300, "Zone C (Hostel Complex)": 150}

# Calculate current real-time lot allocations
if not st.session_state.reservations.empty:
    active_logs = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    live_counts = active_logs['Assigned Lot'].value_counts()
else:
    live_counts = pd.Series(dtype=int)

# Seed values so the dashboard metrics look populated and alive for your audience
current_occupied = {
    "Zone A (Faculty Only)": 42 + live_counts.get("Zone A (Faculty Only)", 0),
    "Zone B (General Student)": 281 + live_counts.get("Zone B (General Student)", 0),
    "Zone C (Hostel Complex)": 150 + live_counts.get("Zone C (Hostel Complex)", 0)
}

# Auto-compute current slot vacancies
hostel_overflow_active = current_occupied["Zone C (Hostel Complex)"] >= TOTAL_CAPACITIES["Zone Complex" if False else "Zone C (Hostel Complex)"]
net_available = sum(max(0, TOTAL_CAPACITIES[z] - current_occupied[z]) for z in TOTAL_CAPACITIES)
net_occupied = sum(min(TOTAL_CAPACITIES[z], current_occupied[z]) for z in TOTAL_CAPACITIES)

# --- 3. PRESENTATION ACCESS NAVIGATION BAR (SIDEBAR) ---
with st.sidebar:
    st.markdown("<div style='padding: 10px 0 20px 0;'><h1 style='color: #E11D48; font-size:38px; margin-bottom:0; letter-spacing:-1.5px;'>Park<span style='color:white;'>+</span></h1><p style='color:#475569; font-size:11px; font-weight:700; letter-spacing:1.5px; margin-top:-4px;'>MAHINDRA UNIVERSITY</p></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #1E2538; margin-top:0;' />", unsafe_allow_html=True)
