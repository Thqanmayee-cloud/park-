import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURATION & ULTRALIGHT GLASSMORPHIC STYLE MATRIX ---
st.set_page_config(
    page_title="Park+ Infrastructure Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Deep high-contrast workspace theme styling overriding default containers
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0B0E14;
        font-family: 'Inter', sans-serif;
        color: #F2F4F4;
    }
    
    /* Premium Sidebar */
    [data-testid="stSidebar"] {
        background-color: #11151F !important;
        border-right: 1px solid #1F2635;
    }
    
    /* Interactive Dashboard Grid Cards */
    div.glass-card {
        background: rgba(20, 26, 38, 0.8);
        border: 1px solid rgba(221, 27, 34, 0.2);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(12px);
        margin-bottom: 25px;
    }
    
    div.metric-box {
        background: #161C2A;
        border-top: 1px solid #28334E;
        border-right: 1px solid #28334E;
        border-bottom: 1px solid #28334E;
        border-left: 4px solid #DD1B22;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.3);
    }
    
    /* Enterprise CTA Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #DD1B22 0%, #A31015 100%);
        color: white !not inline;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        border-radius: 10px !important;
        border: none !important;
        padding: 12px 28px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 18px rgba(221, 27, 34, 0.35);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(221, 27, 34, 0.55);
        background: linear-gradient(135deg, #F9242D 0%, #DD1B22 100%);
    }
    
    /* Dynamic Form Component Inputs */
    input, select, .stSelectbox, div[data-baseweb="select"] {
        background-color: #161C2A !important;
        color: white !important;
        border: 1px solid #28334E !important;
        border-radius: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #7F8C8D !important;
    }
    .stTabs [aria-selected="true"] {
        color: #DD1B22 !important;
        font-weight: 600;
    }
    
    /* Clean UI Overrides */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- ENGINE SESSION STATE ARCHITECTURE ---
if 'reservations' not in st.session_state:
    st.session_state.reservations = pd.DataFrame(columns=['Vehicle Number', 'Role', 'Zone', 'Timestamp', 'Status'])
if 'event_mode' not in st.session_state:
    st.session_state.event_mode = "Standard Operations"
if 'dynamic_switch' not in st.session_state:
    st.session_state.dynamic_switch = True
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = "Student"
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

# Secure credentials registry mapping
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "student": {"emails": ["studentmail@mahindrauniversity.edu.in"], "password": "password123"},
        "faculty": {"emails": ["facultymail@mahindrauniversity.edu.in"], "password": "faculty123"},
        "admin": {"emails": ["admin@mahindrauniversity.edu.in"], "password": "admin123"}
    }

# Constant baseline metrics
ZONE_CAPACITIES = {"Zone A (Faculty)": 50, "Zone B (Students)": 300, "Zone C (Hostel Space)": 150}

# Processing structural math data dynamically based on active reservation log inputs
if not st.session_state.reservations.empty:
    active_res = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    res_counts = active_res['Zone'].value_counts()
else:
    res_counts = pd.Series(dtype=int)

zone_occupied = {
    "Zone A (Faculty)": 44 + res_counts.get("Zone A", 0),
    "Zone B (Students)": 282 + res_counts.get("Zone B", 0),
    "Zone C (Hostel Space)": 150 + res_counts.get("Zone C", 0)
}

# Auto-compute overflow mechanics
is_hostel_full = zone_occupied["Zone C (Hostel Space)"] >= ZONE_CAPACITIES["Zone C (Hostel Space)"]
if st.session_state.dynamic_switch and is_hostel_full:
    zone_occupied["Zone B (Students)"] += 1  # Simulated increment for visual rendering balance

total_available = sum(max(0, ZONE_CAPACITIES[z] - zone_occupied[z]) for z in ZONE_CAPACITIES)
total_occupied = sum(min(ZONE_CAPACITIES[z], zone_occupied[z]) for z in ZONE_CAPACITIES)

# --- IDENTITY ACCESS GATEWAY (SIDEBAR) ---
with st.sidebar:
    st.markdown("<div style='padding: 15px 0 5px 0;'><h1 style='color: #DD1B22; font-size:34px; font-weight:800; margin-bottom:0; letter-spacing:-1px;'>Park<span style='color:white;'>+</span></h1><p style='color:#626F86; font-size:11px; font-weight:600; letter-spacing:1.5px;'>MAHINDRA UNIVERSITY TERMINAL</p></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #1F2635; margin-top:5px;' />", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:12px; color:#97A3B6; font-weight:600; letter-spacing:0.5px; margin-bottom:12px;'>🔐 SECURE PORTAL CLEARANCE</p>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        auth_tabs = st.tabs(["Sign In", "Update Code"])
        
        with auth_tabs[0]:
            role_select = st.selectbox("Account Level", ["Student", "Faculty Member", "Global Administrator"])
            input_email = st.text_input("University Email", key="login_email", placeholder="user@mahindrauniversity.edu.in").strip().lower()
            input_pass = st.text_input("Passkey Sequence", type="password", key="login_pass", placeholder="••••••••")
            
            if st.button("Request Account Verification"):
                if not input_email.endswith("@mahindrauniversity.edu.in"):
                    st.error("Domain Rejected: Explicitly use your @mahindrauniversity.edu.in address.")
                else:
                    authenticated = False
                    if role_select == "Student":
                        if input_email in st.session_state.user_db["student"]["emails"] and input_pass == st.session_state.user_db["student"]["password"]:
                            authenticated = True
                            st.session_state.user_role = "Student"
                    elif role_select == "Faculty Member":
                        if input_email in st.session_state.user_db["faculty"]["emails"] and input_pass == st.session_state.user_db["faculty"]["password"]:
                            authenticated = True
                            st.session_state.user_role = "Faculty Member"
                    elif role_select == "Global Administrator":
                        if input_email in st.session_state.user_db["admin"]["emails"] and input_pass == st.session_state.user_db["admin"]["password"]:
                            authenticated = True
                            st.session_state.user_role = "Global Administrator"

                    if authenticated:
                        st.session_state.user_id = input_email
                        st.session_state.logged_in = True
                        st.success("Authorized successfully!")
                        st.rerun()
                    else:
                        st.error("Clearance Refused: Invalid token match configuration.")
                        
        with auth_tabs[1]:
            target_role = st.selectbox("Target Node", ["Student", "Faculty Member", "Global Administrator"], key="reset_role")
            reset_email = st.text_input("Confirm Account Email", key="reset_email").strip().lower()
            old_pass = st.text_input("Current Secret Key", type="password", key="old_pass")
            new_pass = st.text_input("Configure New Passkey", type="password", key="new_pass")
            
            if st.button("Commit Overwrite changes"):
                db_key = "student" if target_role == "Student" else ("faculty" if target_role == "Faculty Member" else "admin")
                if reset_email in st.session_state.user_db[db_key]["emails"] and old_pass == st.session_state.user_db[db_key]["password"]:
                    if len(new_pass) >= 6:
                        st.session_state.user_db[db_key]["password"] = new_pass
                        st.success("🔒 Local cryptographic ledger re-aligned.")
                    else:
                        st.error("Protocol Rule: Keys must consist of 6 or more characters.")
                else:
                    st.error("Mismatch: System verification parameters failed.")
    else:
        st.markdown(f"""
            <div style='background:#161C2A; padding:16px; border-radius:12px; border: 1px solid #28334E; margin-bottom:15px;'>
                <span style='color:#626F86; font-size:10px; font-weight:700; letter-spacing:1px;'>ACTIVE CONTEXT UNLOCKED</span>
                <h4 style='margin:4px 0 0 0; color:#DD1B22; font-size:16px; font-weight:600;'>{st.session_state.user_id.split('@')[0].upper()}</h4>
                <p style='margin:2px 0 0 0; font-size:12px; color:#A3AED0;'>Clearance: {st.session_state.user_role}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Disconnect Session"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<hr style='border-color: #1F2635;' />", unsafe_allow_html=True)
    
    # SYSTEM CONTROLLER LOGIC (Enforces rule that Admin Console is hidden unless authenticated)
    if st.session_state.logged_in and st.session_state.user_role == "Global Administrator":
        st.markdown("<p style='font-size:12px; color:#97A3B6; font-weight:600; letter-spacing:0.5px;'>🎛️ CORE SUBSYSTEM NAVIGATOR</p>", unsafe_allow_html=True)
        app_mode = st.radio("Select Active Workspace Frame", ["🖥️ Admin Infrastructure Console", "📱 Client Mobile Framework View"])
    else:
        app_mode = "📱 Client Mobile Framework View"

# ==================================================================================
# FRAME WORKSPACE 1: ADMIN INFRASTRUCTURE DASHBOARD PANEL (HIDDEN/SECURE BY DEFAULT)
# ==================================================================================
if app_mode == "🖥️ Admin Infrastructure Console":
    st.markdown("<h1 style='font-size:32px; font-weight:700; letter-spacing:-0.5px; margin-bottom:0;'>🖥️ Infrastructure Routing & Operations Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#626F86; margin-top:-5px; font-size:14px;'>Live macro campus transit array telemetry monitoring hub.</p>", unsafe_allow_html=True)
    
    # NOTIFICATIONS SUBSYSTEM
    st.markdown("<h4 style='font-size:15px; font-weight:600; color:#97A3B6; margin-bottom:10px;'>🔔 LIVE CRITICAL OVERWATCH ALERTS</h4>", unsafe_allow_html=True)
    if is_hostel_full:
        if st.session_state.dynamic_switch:
            st.warning("🔄 **Elastic Structural Override Triggered:** Sector C has breached raw max capacity metrics. AI Core Routing Engine is now handling traffic distribution by absorbing student spillover requests safely into the Sector B cluster matrix.")
        else:
            st.error("🚨 **Critical Load Alert:** Sector C grid capacity metrics read 100% full. System deadlock imminent unless dynamic structural reallocation protocols are engaged via configuration parameters.")
            
    if st.session_state.event_mode == "Placement Drive 2026":
        st.info("📅 **Corporate Event Mode Trigger:** Premium building proximity spaces inside Sector A have been locked down exclusively for visiting talent recruiters and external dignitaries.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # PARKING AVAILABILITY COUNTER METRICS
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.markdown(f"<div class='metric-box'><span style='color:#626F86; font-size:12px; font-weight:600;'>DYNAMIC GRID SLOTS OPEN</span><h2 style='margin:0; font-size:38px; font-weight:700; color:#2ECC71;'>{total_available}</h2></div>", unsafe_allow_html=True)
    with col_metric2:
        st.markdown(f"<div class='metric-box'><span style='color:#626F86; font-size:12px; font-weight:600;'>TOTAL OCCUPIED SLOTS</span><h2 style='margin:0; font-size:38px; font-weight:700; color:#E74C3C;'>{total_occupied}</h2></div>", unsafe_allow_html=True)
    with col_metric3:
        st.markdown(f"<div class='metric-box'><span style='color:#626F86; font-size:12px; font-weight:600;'>TOTAL REGISTERED INSTANCES</span><h2 style='margin:0; font-size:38px; font-weight:700; color:#3498DB;'>{sum(ZONE_CAPACITIES.values())}</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_dash_left, col_dash_right = st.columns([2, 1])

    with col_dash_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:600; color:#FFF;'>⚙️ Cloud Engine Optimization Policies</h3>", unsafe_allow_html=True)
        col_rule1, col_rule2 = st.columns(2)
        with col_rule1:
            st.session_state.dynamic_switch = st.toggle("Enable Automation Spillover Control", value=st.session_state.dynamic_switch)
            st.caption("Instructs algorithms to dynamically alter target lane parameters during high traffic spikes.")
        with col_rule2:
            st.session_state.event_mode = st.selectbox("Global Campus State Matrix Override", ["Standard Operations", "Placement Drive 2026", "Annual Tech Fest"])
            st.caption("Resets spatial restrictions globally to accommodate events.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:600; color:#FFF;'>📈 Live AI Predictive Volume Matrix (Next 12hr Peak Forecast)</h3>", unsafe_allow_html=True)
        chart_data = pd.DataFrame(
            np.random.randint(68, 97, size=(12, 2)),
            columns=['AI Network Load Forecast %', 'Baseline Validation Target %'],
            index=[f"{i}:00" for i in range(9, 21)]
        )
        st.line_chart(chart_data)
        st.caption("🔮 **Machine Learning Core Diagnostics:** Predictive parsing engines indicate localized peak loads shifting due to final exam cycles.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_dash_right:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:600; color:#FFF;'>🗺️ Real-time Sector Densities</h3>", unsafe_allow_html=True)
        
        for zone, cap in ZONE_CAPACITIES.items():
            occupied = zone_occupied[zone]
            pct = min(1.0, occupied / cap)
            status_tag = " — <span style='color:#E74C3C; font-weight:700;'>OVERFLOW ACTIVE</span>" if ("Hostel" in zone and is_hostel_full) else ""
            st.markdown(f"<p style='margin-bottom:4px; font-size:13px; color:#A3AED0;'><b>{zone}</b>: {min(occupied, cap)} / {cap} Nodes{status_tag}</p>", unsafe_allow_html=True)
            st.progress(pct)
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<h4 style='font-size:14px; font-weight:600; margin-bottom:8px; color:#97A3B6;'>📋 CENTRAL DATABASE AUDIT LOGS</h4>", unsafe_allow_html=True)
        st.dataframe(st.session_state.reservations, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==================================================================================
# FRAME WORKSPACE 2: CLIENT MOBILE SMARTPHONE APP FRAMEWORK VIEW
# ==================================================================================
else:
    st.markdown("<div style='text-align:center; padding-top: 10px;'><h2 style='color:#DD1B22; font-weight:800; margin-bottom:0; letter-spacing:-0.5px;'>📱 USER INTERFACE APPLICATION</h2><p style='color:#626F86; font-size:13px; margin-top:-4px;'>HIGH FIDELITY MOCK MOBILE ENVIRONMENT</p></div>", unsafe_allow_html=True)
    
    _, mock_phone, _ = st.columns([1, 1.4, 1])
    
    with mock_phone:
        if not st.session_state.logged_in:
            st.markdown("""
                <div style='background:#141A26; padding:35px 25px; border-radius:20px; border: 1px solid rgba(221,27,34,0.35); text-align:center; box-shadow: 0 15px 45px rgba(0,0,0,0.5);'>
                    <div style='font-size:40px; margin-bottom:10px;'>🔒</div>
                    <h3 style='color:#DD1B22; margin-top:0; font-size:20px; font-weight:700;'>Device Ecosystem Locked</h3>
                    <p style='color:#A3AED0; font-size:13px; line-height:1.5;'>Please authenticate your university identity parameters within the security gateway panel located on the left sidebar context menu to generate booking access tokens.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("""
            ⚙️ **Sandbox Environment Test Parameters:**
            * **Student Access:** `studentmail@mahindrauniversity.edu.in` (Pass: `password123`)
            * **Faculty Access:** `facultymail@mahindrauniversity.edu.in` (Pass: `faculty123`)
            """)
        else:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:700; text-align:center; color:#DD1B22; letter-spacing:-0.5px;'>🚗 SMART SPACE RESERVATION SYSTEM</h3>", unsafe_allow_html=True)
            
            # ZONE ALLOCATION LOGIC ALGORITHMS BASED ON LOGIN IDENTIFICATION
            if st.session_state.user_role == "Faculty Member":
                st.markdown("<div style='background:rgba(46,204,113,0.1); border: 1px solid #2ECC71; padding:12px; border-radius:8px; font-size:12px; margin-bottom:15px; color:#2ECC71; line-height:1.4;'>🎖️ <b>Faculty Matrix Routing Active:</b> Premium frontline building access channels in Zone A are successfully unlocked for your profile layer.</div>", unsafe_allow_html=True)
                selectable_zones = ["Zone A", "Zone B"]
            elif st.session_state.event_mode == "Placement Drive 2026":
                st.markdown("<div style='background:rgba(231,76,60,0.1); border: 1px solid #E74C3C; padding:12px; border-radius:8px; font-size:12px; margin-bottom:15px; color:#E74C3C; line-height:1.4;'>⚠️ <b>Event Matrix Constraint Override:</b> Recruitment guidelines have temporarily restricted Zone A access. Transit rerouting all standard vehicles directly to alternate complex points.</div>", unsafe_allow_html=True)
                selectable_zones = ["Zone B", "Zone C"]
            else:
                st.markdown("<div style='background:rgba(52,152,219,0.1); border: 1px solid #3498DB; padding:12px; border-radius:8px; font-size:12px; margin-bottom:15px; color:#3498DB; line-height:1.4;'>ℹ️ <b>Standard Operations Mode:</b> Please specify your preferred grid parking destination from available lots below.</div>", unsafe_allow_html=True)
                selectable_zones = ["Zone A", "Zone B", "Zone C"]

            vehicle_num = st.text_input("Vehicle Registration License Plate", placeholder="e.g., TS07XX1234").upper()
            target_zone = st.selectbox("Select Target Cluster Lane Target", selectable_zones)
            
            if st.button("Finalize Spatial Reservation"):
                if vehicle_num:
                    new_log = pd.DataFrame([{
                        'Vehicle Number': vehicle_num,
                        'Role': st.session_state.user_role,
                        'Zone': target_zone,
                        'Timestamp': datetime.datetime.now().strftime("%I:%M %p"),
                        'Status': 'Active'
                    }])
                    st.session_state.reservations = pd.concat([st.session_state.reservations, new_log], ignore_index=True)
                    
                    st.balloons()
                    st.success("🎉 Asset Allocation Secured and Reserved!")
                    
                    st.markdown("<hr style='border-color: #28334E;' />", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:13px; font-weight:700; color:#FFF; margin-bottom:4px;'>🗺️ WAYFINDING INTERACTIVE INSTRUCTIONS</p>", unsafe_allow_html=True)
                    st.markdown(f"<div style='background:#161C2A; padding:14px; border-radius:8px; border-left:4px solid #3498DB; font-size:12px; color:#D5DBDB; line-height:1.4;'>📍 <b>Routing Engine Path:</b> Enter through University Main Gate 2. Maintain course straight ahead past academic Block 3, then track visual road indicators directly into assigned structural bays in <b>{target_zone}</b>.</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:12px; font-weight:700; text-align:center; margin-bottom:6px; color:#97A3B6; letter-spacing:0.5px;'>🎫 SECURE GATE ENTRY VALIDATION EMBED</p>", unsafe_allow_html=True)
                    
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={vehicle_num}_{target_zone}&color=dd1b22&bgcolor=161c2a"
                    st.markdown(f"<div style='text-align:center;'><img src='{qr_url}' style='border: 1px solid #28334E; border-radius:12px; padding:12px; background:#161C2A;' width='130'/></div>", unsafe_allow_html=True)
                else:
                    st.error("Input Failure: Explicit identification text parameters required to initialize system parking tokens.")
            st.markdown("</div>", unsafe_allow_html=True)
