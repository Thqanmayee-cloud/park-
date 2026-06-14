import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURATION & PREMIUM GRAPHITE-OBSIDIAN SYSTEM UI ---
st.set_page_config(
    page_title="Park+ Infrastructure Core", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Comprehensive premium look injection - high fidelity styling for projection displays
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #090B10 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #F8FAFC !important;
    }
    
    /* Elegant Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #10141F !important;
        border-right: 1px solid #1E2538;
    }
    
    /* Modern Micro-Card Architecture */
    div.glass-card {
        background: rgba(17, 22, 34, 0.75);
        border: 1px solid rgba(221, 27, 34, 0.2);
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(16px);
        margin-bottom: 25px;
        transition: border 0.3s ease;
    }
    div.glass-card:hover {
        border: 1px solid rgba(221, 27, 34, 0.4);
    }
    
    div.metric-box {
        background: linear-gradient(145deg, #131926 0%, #182032 100%);
        border: 1px solid #232D44;
        border-top: 3px solid #DD1B22;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 6px 30px rgba(0,0,0,0.4);
        text-align: center;
    }
    
    /* Polished Interactive Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #DD1B22 0%, #9E1015 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 28px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        box-shadow: 0 5px 20px rgba(221, 27, 34, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(221, 27, 34, 0.65);
        color: #FFFFFF !important;
    }
    
    /* Form Element Overrides */
    input, select, .stSelectbox, div[data-baseweb="select"] {
        background-color: #131926 !important;
        color: #FFFFFF !important;
        border: 1px solid #232D44 !important;
        border-radius: 10px !important;
        font-size: 14px !important;
    }
    
    label {
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Hide Default Branding Headers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM TELEMETRY ENGINE STATE ---
if 'reservations' not in st.session_state:
    st.session_state.reservations = pd.DataFrame(columns=['Vehicle Number', 'Profile Role', 'Zone Allocation', 'Timestamp', 'Status'])
if 'event_override' not in st.session_state:
    st.session_state.event_override = "Standard Operations"
if 'spillover_protocol' not in st.session_state:
    st.session_state.spillover_protocol = True

# Standardized Parking Lot Space Dimensions
ZONE_CAPACITIES = {"Zone A (Faculty Priority)": 50, "Zone B (General Student)": 300, "Zone C (Hostel Sector)": 150}

# Compute real-time load distribution
if not st.session_state.reservations.empty:
    active_logs = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    live_counts = active_logs['Zone Allocation'].value_counts()
else:
    live_counts = pd.Series(dtype=int)

# Simulating initial structural data fills so metrics feel alive for the presentation audience
live_occupied = {
    "Zone A (Faculty Priority)": 41 + live_counts.get("Zone A (Faculty Priority)", 0),
    "Zone B (General Student)": 279 + live_counts.get("Zone B (General Student)", 0),
    "Zone C (Hostel Sector)": 150 + live_counts.get("Zone C (Hostel Sector)", 0)  # Seed full to showcase notification rules
}

# Auto-compute overflow routing
hostel_is_maxed = live_occupied["Zone C (Hostel Sector)"] >= ZONE_CAPACITIES["Zone C (Hostel Sector)"]

total_available_slots = sum(max(0, ZONE_CAPACITIES[z] - live_occupied[z]) for z in ZONE_CAPACITIES)
total_occupied_slots = sum(min(ZONE_CAPACITIES[z], live_occupied[z]) for z in ZONE_CAPACITIES)

# --- CONTROLS OVERLAY SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='padding: 10px 0;'><h1 style='color: #DD1B22; font-size:36px; font-weight:800; margin-bottom:0; letter-spacing:-1.5px;'>Park<span style='color:white;'>+</span></h1><p style='color:#64748B; font-size:11px; font-weight:600; letter-spacing:1px; margin-top:-2px;'>MAHINDRA UNIVERSITY CORE</p></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #1E2538; margin-top:0;' />", unsafe_allow_html=True)
    
    st.markdown("<h4 style='font-size:12px; color:#94A3B8; font-weight:600; letter-spacing:1px;'>🎛️ PRESENTATION CONSOLE CONTROLS</h4>", unsafe_allow_html=True)
    
    st.session_state.spillover_protocol = st.toggle("Enable Automation Spillover Control", value=st.session_state.spillover_protocol)
    st.session_state.event_override = st.selectbox("Global Campus Event Matrix Overwrite", ["Standard Operations", "Placement Drive 2026", "Annual Tech Fest"])
    
    st.markdown("<hr style='border-color: #1E2538;' />", unsafe_allow_html=True)
    st.caption("💡 **Presentation Tip:** Use these quick sidebar config settings to trigger dynamic notification alerts and modify lot access routes instantly during your live display.")

# ==================================================================================
# SCREEN MAIN PLATFORM DISPLAY FRAMEWORK
# ==================================================================================
st.markdown("<h2 style='font-size:28px; font-weight:800; margin-bottom:0; letter-spacing:-0.5px;'>⚡ High-Fidelity Smart Transit Ecosystem</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:-5px; font-size:14px; margin-bottom:25px;'>Real-time orchestration workspace showcasing mobile user booking execution alongside live cloud management panels.</p>", unsafe_allow_html=True)

layout_col_left, layout_col_right = st.columns([1.1, 2])

# ----------------------------------------------------------------------------------
# LEFT PANEL: HIGH FIDELITY SMARTPHONE USER INTERFACE SIMULATOR
# ----------------------------------------------------------------------------------
with layout_col_left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding-bottom:15px;'><span style='background:rgba(221,27,34,0.1); color:#DD1B22; font-size:11px; font-weight:700; padding:4px 12px; border-radius:20px; letter-spacing:0.5px;'>MOBILE VIEW ENDPOINT</span></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-size:20px; font-weight:700; text-align:center;'>🚗 Secure Slot Reservation</h3>", unsafe_allow_html=True)
    
    # Active role selection acting as a replacement for credentials logins
    simulated_role = st.radio("Select Simulated Identity Profile", ["Student Mode", "Faculty Member Mode"], horizontal=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # PRIORITY ALLOCATION LOGIC CODES BASED ON SIMULATOR ROLES
    if simulated_role == "Faculty Member Mode":
        st.markdown("<div style='background:rgba(46,204,113,0.08); border: 1px solid #2ECC71; padding:12px; border-radius:10px; font-size:12px; margin-bottom:15px; color:#2ECC71; line-height:1.4;'>🎖️ <b>Faculty Priority Mode Active:</b> Premium building access vectors within <b>Zone A</b> have been prioritized and unlocked for selection.</div>", unsafe_allow_html=True)
        unlocked_sectors = ["Zone A (Faculty Priority)", "Zone B (General Student)"]
    elif st.session_state.event_override == "Placement Drive 2026":
        st.markdown("<div style='background:rgba(231,76,60,0.08); border: 1px solid #E74C3C; padding:12px; border-radius:10px; font-size:12px; margin-bottom:15px; color:#E74C3C; line-height:1.4;'>⚠️ <b>Corporate Event Matrix Active:</b> Zone A has been reserved for enterprise guest profiles. Standard routes redirected to student complexes.</div>", unsafe_allow_html=True)
        unlocked_sectors = ["Zone B (General Student)", "Zone C (Hostel Sector)"]
    else:
        st.markdown("<div style='background:rgba(52,152,219,0.08); border: 1px solid #3498DB; padding:12px; border-radius:10px; font-size:12px; margin-bottom:15px; color:#3498DB; line-height:1.4;'>ℹ️ <b>Standard Operations:</b> Input vehicle configurations to lease an open terminal node spot.</div>", unsafe_allow_html=True)
        unlocked_sectors = ["Zone B (General Student)", "Zone C (Hostel Sector)"]

    input_plate = st.text_input("Vehicle Registration License String", placeholder="e.g., TS07XX1234").upper()
    selected_sector = st.selectbox("Target Sector Matrix Grid", unlocked_sectors)
    
    if st.button("Confirm Terminal Reservation"):
        if input_plate:
            new_booking = pd.DataFrame([{
                'Vehicle Number': input_plate,
                'Profile Role': simulated_role.replace(" Mode", ""),
                'Zone Allocation': selected_sector,
                'Timestamp': datetime.datetime.now().strftime("%I:%M %p"),
                'Status': 'Active'
            }])
            st.session_state.reservations = pd.concat([st.session_state.reservations, new_booking], ignore_index=True)
            
            st.balloons()
            st.success("🎉 Asset Spot Lease Successfully Registered!")
            
            st.markdown("<hr style='border-color: #232D44;' />", unsafe_allow_html=True)
            st.markdown("<p style='font-size:12px; font-weight:700; color:#FFF; margin-bottom:4px;'>🗺️ SYSTEM TURN-BY-TURN ROUTING DIRECTION</p>", unsafe_allow_html=True)
            st.markdown(f"<div style='background:#131926; padding:12px; border-radius:8px; border-left:4px solid #3498DB; font-size:12px; color:#94A3B8; line-height:1.4;'>Proceed via Campus Gate 2. Continue past academic complex Block 3, then follow red floor vectors pointing straight into <b>{selected_sector}</b>.</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            # Dynamic QR generation block matching crimson palette lines
            qr_embed_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={input_plate}_{selected_sector}&color=dd1b22&bgcolor=131926"
            st.markdown(f"<div style='text-align:center;'><p style='font-size:11px; font-weight:700; color:#64748B; margin-bottom:6px;'>DIGITAL ACCESS PERMIT TERMINAL CERTIFICATE</p><img src='{qr_embed_url}' style='border: 1px solid #232D44; border-radius:12px; padding:10px; background:#131926;' width='120'/></div>", unsafe_allow_html=True)
        else:
            st.error("Submission Halted: Please populate a valid license validation string.")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------
# RIGHT PANEL: EXECUTIVE INFRASTRUCTURE MONITORING COMMAND CENTER
# ----------------------------------------------------------------------------------
with layout_col_right:
    # SYSTEM NOTIFICATIONS BLOCK
    if hostel_is_maxed:
        if st.session_state.spillover_protocol:
            st.warning("🔄 **Dynamic Resource Optimization Warning:** Sector C volume capacity has crossed critical metrics thresholds. Infrastructure rules have activated an automated elastic overflow matrix, shifting subsequent arrivals directly into Zone B loops.")
        else:
            st.error("🚨 **Capacity Exception System Warning:** Sector C metrics read 100% full. Parking structural lockout in effect until overflow balancing controls are enabled via admin settings.")
            
    if st.session_state.event_override == "Placement Drive 2026":
        st.info("📅 **Corporate Event Overwrite Rule Triggered:** Zone A capacity is locked down exclusively to service official placement recruitment vehicles.")

    # PARKING AVAILABILITY METRICS GRID ROW
    st.markdown("<div style='margin-bottom: 20px;'><h4 style='font-size:12px; color:#94A3B8; font-weight:600; letter-spacing:1px; margin-bottom:10px;'>📊 GLOBAL INFRASTRUCTURE PARKING AVAILABILITY</h4></div>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown(f"<div class='metric-box'><span style='color:#64748B; font-size:11px; font-weight:600;'>OPEN TERMINAL NODES</span><h2 style='margin:0; font-size:36px; font-weight:800; color:#2ECC71;'>{total_available_slots}</h2></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='metric-box'><span style='color:#64748B; font-size:11px; font-weight:600;'>OCCUPIED BAY SECTORS</span><h2 style='margin:0; font-size:36px; font-weight:800; color:#E74C3C;'>{total_occupied_slots}</h2></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='metric-box'><span style='color:#64748B; font-size:11px; font-weight:600;'>TOTAL CONNECTED BAY CAP</span><h2 style='margin:0; font-size:36px; font-weight:800; color:#3498DB;'>{sum(ZONE_CAPACITIES.values())}</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ZONE ALLOCATION PROGRESS METERS
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:700; color:#FFF;'>🗺️ Real-time Sector Capacity Metrics</h3>", unsafe_allow_html=True)
    
    for zone, max_cap in ZONE_CAPACITIES.items():
        current_occupied = live_occupied[zone]
        fill_ratio = min(1.0, current_occupied / max_cap)
        
        # Color coding string metrics tags matching system loads
        if fill_ratio >= 0.95:
            load_label = "<span style='color:#E74C3C; font-weight:700;'>CRITICAL DENSITY</span>"
        elif fill_ratio >= 0.75:
            load_label = "<span style='color:#F39C12; font-weight:700;'>HIGH VOLUME</span>"
        else:
            load_label = "<span style='color:#2ECC71; font-weight:700;'>STABLE LOAD</span>"
            
        st.markdown(f"<p style='margin-bottom:5px; font-size:13px; color:#CBD5E1;'><b>{zone}</b>: {min(current_occupied, max_cap)} / {max_cap} slots — {load_label}</p>", unsafe_allow_html=True)
        st.progress(fill_ratio)
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # DEMAND AI PREDICTIONS
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:700; color:#FFF;'>📈 Live AI Predictive Volume Matrix (Next 12hr Horizon Forecast)</h3>", unsafe_allow_html=True)
    
    predictive_chart_data = pd.DataFrame(
        np.random.randint(70, 96, size=(12, 2)),
        columns=['AI Predictive Model Engine Load %', 'Historical Base Line Average %'],
        index=[f"{hour}:00" for hour in range(9, 21)]
    )
    st.line_chart(predictive_chart_data)
    st.caption("🔮 **Neural Forecast Summary:** Internal prediction models indicate localized peak surges incoming from student vehicle matrices around 11:30 AM based on class schedule historical logs.")
    st.markdown("</div>", unsafe_allow_html=True)

    # DATA BALANCING SYSTEM AUDIT TRAILS
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-size:16px; font-weight:700; color:#FFF;'>📋 Cloud Terminal Live Master Audit Trail</h3>", unsafe_allow_html=True)
    st.dataframe(st.session_state.reservations, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
