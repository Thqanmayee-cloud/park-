import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- 1. GLOBAL ENVIRONMENT CONFIGURATION ---
st.set_page_config(
    page_title="Park+ Infrastructure Management Core", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# --- 2. LUXURY PRESENTATION VISUAL THEME OVERHAUL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Premium High-Contrast Canvas */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0B0E14 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #F8FAFC !important;
    }
    
    /* Clean Enterprise Top Header Navigation Element */
    .brand-banner {
        background: linear-gradient(90deg, #111622 0%, #1A2235 100%);
        border-left: 5px solid #E11D48;
        padding: 20px 25px;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* Beautiful Content Layout Containers */
    .dashboard-panel {
        background-color: #111622;
        border: 1px solid #1F293D;
        padding: 22px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    
    /* Status Warning/Info Notification Overrides */
    .custom-alert {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-left: 4px solid #F59E0B;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #E2E8F0;
    }
    
    /* Presentation Numeric Statistics Display Blocks */
    .metric-card {
        background: linear-gradient(145deg, #151C2C 0%, #0E1320 100%);
        border: 1px solid #222D46;
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* High-Vibrancy Call To Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px !not inline;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 22px rgba(225, 29, 72, 0.5);
    }
    
    /* Input field label styles */
    label {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Strip default platform headers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- 3. CORE REAL-TIME DATA DATABASE STATE ---
if 'reservations' not in st.session_state:
    st.session_state.reservations = pd.DataFrame(columns=['Vehicle Plate', 'Profile Type', 'Assigned Zone', 'Timestamp', 'Status'])

# Fixed capacity rules for Mahindra University zones
ZONE_CONSTRAINTS = {"Zone A (Faculty Priority)": 50, "Zone B (General Student)": 300, "Zone C (Hostel Sector)": 150}

# Parse runtime log entries
if not st.session_state.reservations.empty:
    active_logs = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    live_counts = active_logs['Assigned Zone'].value_counts()
else:
    live_counts = pd.Series(dtype=int)

# Pre-populating metrics data so that the dashboard feels completely live and organic during the presentation
current_occupied = {
    "Zone A (Faculty Priority)": 44 + live_counts.get("Zone A (Faculty Priority)", 0),
    "Zone B (General Student)": 284 + live_counts.get("Zone B (General Student)", 0),
    "Zone C (Hostel Sector)": 150 + live_counts.get("Zone C (Hostel Sector)", 0) # Hardcoded full to show automated spillover logic
}

# Calculated operational statuses
is_hostel_maxed = current_occupied["Zone C (Hostel Sector)"] >= ZONE_CONSTRAINTS["Zone C (Hostel Sector)"]
total_vacant = sum(max(0, ZONE_CONSTRAINTS[z] - current_occupied[z]) for z in ZONE_CONSTRAINTS)
total_filled = sum(min(ZONE_CONSTRAINTS[z], current_occupied[z]) for z in ZONE_CONSTRAINTS)

# --- 4. TOP APPLICATION NAVIGATION HEADER BAR ---
st.markdown("""
    <div class="brand-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin:0; font-size:28px; font-weight:800; color:#FFF; letter-spacing:-1px;">Park<span style="color:#E11D48;">+</span> Infrastructure Management Terminal</h1>
                <p style="margin:2px 0 0 0; color:#64748B; font-size:12px; font-weight:600; letter-spacing:0.5px;">MAHINDRA UNIVERSITY INTEGRATED COMMAND CONTROL ROOM</p>
            </div>
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; color: #10B981; padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight:700; letter-spacing:0.5px;">
                ● LIVE CAMPUS SENSOR ARRAYS ONLINE
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==================================================================================
# --- 5. THE ALL-IN-ONE MASTER SPLIT VIEW GRID ---
# ==================================================================================
col_left_simulator, col_right_dashboard = st.columns([1, 1.4])

# ----------------------------------------------------------------------------------
# LEFT PANEL: CLIENT INTERACTIVE SMARTPHONE APP & RESERVATION ENGINE
# ----------------------------------------------------------------------------------
with col_left_simulator:
    st.markdown('<h3 style="color:#FFF; font-size:18px; margin-bottom:15px; border-bottom: 2px solid #1F293D; padding-bottom:8px;">📱 End-User Smart Booking App</h3>', unsafe_allow_html=True)
    
    # FEATURE 6: NOTIFICATIONS SUBSYSTEM
    if is_hostel_maxed:
        st.markdown("""
            <div class="custom-alert">
                <span style="color: #F59E0B; font-weight: 700; font-size:13px; display:block; margin-bottom:2px;">⚠️ SYSTEM NOTIFICATION: SPILLOVER OVERRIDE ENGAGED</span>
                Hostel Complex (Zone C) load metrics have breached 100%. Dynamic system routing guidelines are now transferring newly issued student vehicle vectors automatically into alternative Zone B slots.
            </div>
        """, unsafe_allow_html=True)

    # FEATURE 2: PARKING RESERVATION USER INPUT CAPTURE
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color:#E11D48; font-size:15px;'>⚡ Secure Allocation Gateway</h4>", unsafe_allow_html=True)
    
    user_identity = st.selectbox("Specify Identity Profile Classification", ["Student Profile Mode", "Faculty Representative Mode"])
    
    # FEATURE 5: ZONE ALLOCATION & PRIORITY ALLOCATION ENGINE FOR FACULTY
    if user_identity == "Faculty Representative Mode":
        selectable_zones = ["Zone A (Faculty Priority)", "Zone B (General Student)"]
        st.markdown("<div style='background:rgba(16, 185, 129, 0.08); border:1px solid #10B981; color:#10B981; padding:10px; border-radius:8px; font-size:12px; margin-bottom:15px;'>🎖️ <b>Faculty Priority Mapping:</b> Secure proximity lanes inside premium Zone A are cleared for your profile.</div>", unsafe_allow_html=True)
    else:
        selectable_zones = ["Zone B (General Student)", "Zone C (Hostel Sector)"]
        st.markdown("<div style='background:rgba(148, 163, 184, 0.05); border:1px solid #475569; color:#94A3B8; padding:10px; border-radius:8px; font-size:12px; margin-bottom:15px;'>ℹ️ Standard vehicle profiles are assigned layout positions across student and housing zones.</div>", unsafe_allow_html=True)
        
    license_plate = st.text_input("Vehicle License Registration Plate", placeholder="e.g., TS07XX1234").upper()
    target_zone_selection = st.selectbox("Choose Target Sector Core", selectable_zones)
    
    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    
    # EXECUTE RESERVATION DATA COMMIT
    if st.button("Finalize Spot Lease Allocation"):
        if license_plate:
            new_log_entry = pd.DataFrame([{
                'Vehicle Plate': license_plate,
                'Profile Type': user_identity.replace(" Mode", ""),
                'Assigned Zone': target_zone_selection,
                'Timestamp': datetime.datetime.now().strftime("%I:%M %p"),
                'Status': 'Active'
            }])
            st.session_state.reservations = pd.concat([st.session_state.reservations, new_log_entry], ignore_index=True)
            st.balloons()
            st.success("Space Reserved! Asset permit pushed down to ledger stream.")
            st.rerun()
        else:
            st.error("Input Halting error: A valid license plate parameter must be provided.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # PASS GENERATION VIEWER SCREEN
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-size:14px; color:#FFF;'>🎫 Active Gateway Security Ticket</h4>", unsafe_allow_html=True)
    if not st.session_state.reservations.empty:
        active_pass = st.session_state.reservations.iloc[-1]
        st.markdown(f"""
            <div style="font-size:13px; color:#CBD5E1; line-height:1.6;">
                <b>Vehicle Plate Target:</b> <span style="color:#E11D48;">{active_pass['Vehicle Plate']}</span><br>
                <b>Assigned Sector Core:</b> {active_pass['Assigned Zone']}<br>
                <b>Route Map:</b> Enter Gate 2 ➔ Keep straight past Block 3 ➔ Follow signs into your row.
            </div>
        """, unsafe_allow_html=True)
        qr_service_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={active_pass['Vehicle Plate']}_{active_pass['Assigned Zone']}&color=e11d48&bgcolor=111622"
        st.markdown(f"<div style='text-align:center; margin-top:15px;'><img src='{qr_service_url}' style='border: 1px solid #1F293D; border-radius:10px;' width='110'/></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#475569; font-size:12px; margin-bottom:0; text-align:center;'>No active spot leased during this runtime instance yet.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------
# RIGHT PANEL: CENTRAL EXECUTIVE ADMIN MANAGEMENT DASHBOARD CORE
# ----------------------------------------------------------------------------------
with col_right_dashboard:
    st.markdown('<h3 style="color:#FFF; font-size:18px; margin-bottom:15px; border-bottom: 2px solid #1F293D; padding-bottom:8px;">🖥️ Core Subsystem Administration Console</h3>', unsafe_allow_html=True)
    
    # FEATURE 7: PARKING AVAILABILITY SYSTEM METRICS COUNTERS
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.markdown(f'<div class="metric-card"><span style="color:#64748B; font-size:11px; font-weight:700;">VACANT SPACES AVAILABLE</span><h2 style="margin:5px 0 0 0; color:#10B981; font-weight:800; font-size:28px;">{total_vacant}</h2></div>', unsafe_allow_html=True)
    with metric_col2:
        st.markdown(f'<div class="metric-card"><span style="color:#64748B; font-size:11px; font-weight:700;">TOTAL FILLED SLOTS</span><h2 style="margin:5px 0 0 0; color:#EF4444; font-weight:800; font-size:28px;">{total_filled}</h2></div>', unsafe_allow_html=True)
    with metric_col3:
        st.markdown(f'<div class="metric-card"><span style="color:#64748B; font-size:11px; font-weight:700;">CONNECTED TOTAL NETWORK</span><h2 style="margin:5px 0 0 0; color:#3B82F6; font-
