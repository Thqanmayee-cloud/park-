import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURATION & PREMIUM GRAPHITE-OBSIDIAN SYSTEM UI ---
st.set_page_config(
    page_title="Park+ Infrastructure Core", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# Comprehensive presentation redesign styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0D0F14 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #F1F5F9 !important;
    }
    
    /* Elegant Top-Bar Header Simulation */
    div.nav-header {
        background: linear-gradient(90deg, #121620 0%, #1A202C 100%);
        border-bottom: 2px solid #DD1B22;
        padding: 18px 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    /* Clean Cards Architecture */
    div.glass-card {
        background: #121620;
        border: 1px solid #1E2538;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    
    div.metric-box {
        background: #171E2E;
        border: 1px solid #232D44;
        padding: 20px;
        border-radius: 12px;
        text-align: left;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Polished Interactive Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #DD1B22 0%, #B31015 100%) !important;
        color: #FFFFFF !not inline;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(221, 27, 34, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(221, 27, 34, 0.5);
    }
    
    /* Form Element Overrides */
    input, select, .stSelectbox, div[data-baseweb="select"] {
        background-color: #171E2E !important;
        color: #FFFFFF !important;
        border: 1px solid #232D44 !important;
        border-radius: 8px !important;
    }
    
    label {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        letter-spacing: 0.5px;
    }
    
    /* Clean UI Customizations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM TELEMETRY ENGINE STATE ---
if 'reservations' not in st.session_state:
    st.session_state.reservations = pd.DataFrame(columns=['Vehicle Number', 'Profile Role', 'Zone Allocation', 'Timestamp', 'Status'])

ZONE_CAPACITIES = {"Zone A (Faculty Priority)": 50, "Zone B (General Student)": 300, "Zone C (Hostel Sector)": 150}

if not st.session_state.reservations.empty:
    active_logs = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    live_counts = active_logs['Zone Allocation'].value_counts()
else:
    live_counts = pd.Series(dtype=int)

# Real-time baseline data setup
live_occupied = {
    "Zone A (Faculty Priority)": 41 + live_counts.get("Zone A (Faculty Priority)", 0),
    "Zone B (General Student)": 279 + live_counts.get("Zone B (General Student)", 0),
    "Zone C (Hostel Sector)": 150 + live_counts.get("Zone C (Hostel Sector)", 0)
}

hostel_is_maxed = live_occupied["Zone C (Hostel Sector)"] >= ZONE_CAPACITIES["Zone C (Hostel Sector)"]

total_available_slots = sum(max(0, ZONE_CAPACITIES[z] - live_occupied[z]) for z in ZONE_CAPACITIES)
total_occupied_slots = sum(min(ZONE_CAPACITIES[z], live_occupied[z]) for z in ZONE_CAPACITIES)

# --- HEADER APP BRANDING BAR ---
st.markdown("""
    <div class='nav-header'>
        <div>
            <span style='color: #DD1B22; font-size: 26px; font-weight: 800; letter-spacing: -1px;'>Park<span style='color:white;'>+</span></span>
            <span style='color: #64748B; font-size: 12px; font-weight: bold; margin-left: 15px; letter-spacing: 1px;'>MAHINDRA UNIVERSITY COMMAND CORE</span>
        </div>
        <div style='background: rgba(46, 204, 113, 0.1); border: 1px solid #2ECC71; padding: 4px 12px; border-radius: 20px; font-size: 12px; color: #2ECC71; font-weight: 600;'>
            🟢 LIVE NETWORK ONLINE
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NOTIFICATIONS CHANNEL ---
if hostel_is_maxed:
    st.markdown("""
        <div style='background: rgba(243, 156, 18, 0.08); border-left: 4px solid #F39C12; padding: 16px; border-radius: 8px; margin-bottom: 25px;'>
            <h5 style='margin: 0; color: #F39C12; font-weight: 700; font-size: 14px;'>🔄 AUTOMATED SPILLOVER PROTOCOL ACTIVE</h5>
            <p style='margin: 4px 0 0 0; color: #94A3B8; font-size: 13px;'>Sector C has reached max structural limits. Dynamic traffic patterns are actively routing subsequent
