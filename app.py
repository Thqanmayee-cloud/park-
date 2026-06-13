import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime
import re

# --- PREMIUM DASHBOARD THEMING & GLASSMORPHISM ---
st.set_page_config(
    page_title="Park+ Elite Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom CSS injected directly to override standard unstyled blocks
st.markdown("""
    <style>
    /* Global Background & Font Tuning */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0E1117;
        font-family: 'Inter', sans-serif;
        color: #ECF0F1;
    }
    
    /* Elegant Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #161A23 !important;
        border-right: 1px solid #242B3D;
    }
    
    /* Modern Glassmorphic Container Cards */
    div.glass-card {
        background: rgba(25, 30, 41, 0.65);
        border: 1px solid rgba(221, 27, 34, 0.15);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        margin-bottom: 20px;
    }
    
    div.metric-card {
        background: #1A1F2C;
        border-left: 4px solid #DD1B22;
        border-top: 1px solid #2E364A;
        border-right: 1px solid #2E364A;
        border-bottom: 1px solid #2E364A;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Premium Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #DD1B22 0%, #B8141A 100%);
        color: white !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        border-radius: 10px !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(221, 27, 34, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(221, 27, 34, 0.5);
        background: linear-gradient(135deg, #F02830 0%, #DD1B22 100%);
    }
    
    /* Alert Tweaks */
    .stAlert {
        border-radius: 12px !important;
        background-color: #1C2030 !important;
        border: 1px solid #2E364A !important;
    }
    
    /* Input Form Enhancements */
    input, select, .stSelectbox img {
        background-color: #1A1F2C !important;
        color: white !important;
        border: 1px solid #2E364A !important;
        border-radius: 8px !important;
    }
    
    /* Hide Default Streamlit Style Elements for High Fidelity Feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM STATE ENGINE ---
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

# Expanded user registry accepting clean template emails and explicit patterns
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "student": {"emails": ["studentmail@mahindrauniversity.edu.in", "sm25ubbd171@mahindrauniversity.edu.in"], "password": "password123"},
        "faculty": {"emails": ["facultymail@mahindrauniversity.edu.in", "anjali.rajan@mahindrauniversity.edu.in"], "password": "faculty123"},
        "admin": {"emails": ["admin@mahindrauniversity.edu.in"], "password": "admin123"}
    }

ZONE_CAPACITIES = {"Zone A (Faculty)": 50, "Zone B (Students)": 300, "Zone C (Hostel)": 150}

if not st.session_state.reservations.empty:
    active_res = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    res_counts = active_res['Zone'].value_counts()
else:
    res_counts = pd.Series(dtype=int)

zone_occupied = {
    "Zone A (Faculty)": 42 + res_counts.get("Zone A", 0),
    "Zone B (Students)": 285 + res_counts.get("Zone B", 0),
    "Zone C (Hostel)": 150 + res_counts.get("Zone C", 0)
}

if st.session_state.dynamic_switch and zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"]:
    zone_status_c = "⚠️ OVERFLOW ACTIVE"
else:
    zone_status_c = "Critical Load" if zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"] else "Stable"

total_available = sum(max(0, ZONE_CAPACITIES[z] - zone_occupied[z]) for z in ZONE_CAPACITIES)
total_occupied = sum(min(ZONE_CAPACITIES[z], zone_occupied[z]) for z in ZONE_CAPACITIES)

# --- NAVIGATION & AUTH SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='padding: 10px 0;'><h1 style='color: #DD1B22; font-size:32px; font-weight:700; margin-bottom:0;'>Park<span style='color:white;'>+</span></h1><p style='color:#7F8C8D; font-size:12px; letter-spacing:1px;'>MAHINDRA UNIVERSITY ENGINE</p></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #242B3D;' />", unsafe_allow_html=True)
    
    st.markdown("<h3 style='font-size:16px; color:#AEB6BF; font-weight:500;'>🔒 SECURITY IDENTITY GATEWAY</h3>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Update Passphrase"])
        
        with auth_tab1:
            role_select = st.selectbox("Portal Clearances", ["Student", "Faculty Member", "Admin / Security"])
            input_email = st.text_input("University Email ID", key="login_email", placeholder="username@mahindrauniversity.edu.in").strip().lower()
            input_pass = st.text_input("Security Code", type="password", key="login_pass", placeholder="••••••••")
            
            if st.button("Request Authorization"):
                if not input_email.endswith("@mahindrauniversity.edu.in"):
                    st.error("Invalid Domain: Use official MU credentials.")
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
                    elif role_select == "Admin / Security":
                        if input_email in st.session_state.user_db["admin"]["emails"] and input_pass == st.session_state.user_db["admin"]["password"]:
                            authenticated = True
                            st.session_state.user_role = "Admin / Security"

                    if authenticated:
                        st.session_state.user_id = input_email
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Clearance Refused: Check credentials.")
                        
        with auth_tab2:
            target_role = st.selectbox("Target Profile", ["Student", "Faculty Member", "Admin / Security"], key="reset_role")
            reset_email = st.text_input("Confirm Registered Email ID", key="reset_email").strip().lower()
            old_pass = st.text_input("Current Passphrase", type="password", key="old_pass")
            new_pass = st.text_input("Configure New Passphrase", type="password", key="new_pass")
            
            if st.button("Commit Ledger Overwrite"):
                db_key = "student" if target_role == "Student" else ("faculty" if target_role == "Faculty Member" else "admin")
                if reset_email in st.session_state.user_db[db_key]["emails"] and old_pass == st.session_state.user_db[db_key]["password"]:
                    if len(new_pass) >= 6:
                        st.session_state.user_db[db_key]["password"] = new_pass
                        st.success("🔒 System Registry Updated Successfully.")
                    else:
                        st.error("Validation Failed: Code length must be ≥ 6.")
                else:
                    st.error("Data Mismatch: Identity verification rejected.")
    else:
        st.markdown(f"""
            <div style='background:#1A1F2C; padding:15px; border-radius:10px; border: 1px solid #2E364A; margin-bottom:15px;'>
                <span style='color:#7F8C8D; font-size:11px;'>VERIFIED OPERATOR</span>
                <h4 style='margin:0; color:#DD1B22;'>{st.session_state.user_id.split('@')[0].upper()}</h4>
                <p style='margin:0; font-size:12px; color:#BDC3C7;'>Clearance: {st.session_state.user_role}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Terminate Session"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<hr style='border-color: #242B3D;' />", unsafe_allow_html=True)
    if st.session_state.logged_in and st.session_state.user_role == "Admin / Security":
        app_mode = st.radio("SYSTEM VIEW MODE", ["🖥️ Admin Core Console", "📱 Client Mobile Interface"])
    else:
        app_mode = "📱 Client Mobile Interface"

# ==========================================
# MODERN VIEW 1: ADMIN CORE CONSOLE
# ==========================================
if app_mode == "🖥️ Admin Core Console":
    st.markdown("<h1 style='font-size:32px; font-weight:700; letter-spacing:-0.5px;'>🖥️ MU Parking Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#7F8C8D; margin-top:-10px;'>Live architectural infrastructure routing telemetry.</p>", unsafe_allow_html=True)
    
    if zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"]:
        if st.session_state.dynamic_switch:
            st.warning("🔄 **Dynamic Resource Routing Active:** Sector C threshold breached. Elastic allocation routing student parking requests directly into Sector B matrix.")
        else:
            st.error("🚨 **System Cap Warning:** Sector C is at 100% deadweight limit. Grid lockout imminent without dynamic reallocation protocols enabled.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f"<div class='metric-card'><span class='metric-label' style='color:#7F8C8D; font-size:13px;'>DYNAMIC AVAILABLE SLOTS</span><h2 style='margin:0; font-size:36px; font-weight:700; color:#2ECC71;'>{total_available}</h2></div>", unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"<div class='metric-card'><span class='metric-label' style='color:#7F8C8D; font-size:13px;'>TOTAL BUSY BAY ROWS</span><h2 style='margin:0; font-size:36px; font-weight:700; color:#E74C3C;'>{total_occupied}</h2></div>", unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"<div class='metric-card'><span class='metric-label' style='color:#7F8C8D; font-size:13px;'>TOTAL NETWORK CAPACITY</span><h2 style='margin:0; font-size:36px; font-weight:700; color:#3498DB;'>{sum(ZONE_CAPACITIES.values())}</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_dash_left, col_dash_right = st.columns([2, 1])

    with col_dash_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:600;'>⚙️ AI Optimization Policy Engines</h3>", unsafe_allow_html=True)
        col_rule1, col_rule2 = st.columns(2)
        with col_rule1:
            st.session_state.dynamic_switch = st.toggle("Enable Grid Spillover Reallocation", value=st.session_state.dynamic_switch)
            st.caption("Alters algorithmic routing mapping dynamically during high-density block hours.")
        with col_rule2:
            st.session_state.event_mode = st.selectbox("Active Campus Environmental Matrix", ["Standard Operations", "Placement Drive 2026", "Annual Tech Fest"])
            st.caption("Instantly resets sector priority constraints globally.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:600;'>📈 Real-time AI Predictive Traffic Matrix</h3>", unsafe_allow_html=True)
        chart_data = pd.DataFrame(
            np.random.randint(70, 96, size=(12, 2)),
            columns=['AI Network Load Forecast %', 'Baseline Calibration Target %'],
            index=[f"{i}:00" for i in range(9, 21)]
        )
        st.line_chart(chart_data)
        st.caption("🔮 **Neural Network Note:** Expected core cluster surge identified at 11:30 AM based on student class schedules.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_dash_right:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:600;'>🗺️ Sector Grid Densities</h3>", unsafe_allow_html=True)
        
        for zone, cap in ZONE_CAPACITIES.items():
            occupied = zone_occupied[zone]
            pct = min(1.0, occupied / cap)
            status_tag = f" — <span style='color:#E74C3C;'>{zone_status_c}</span>" if "Hostel" in zone else ""
            st.markdown(f"<p style='margin-bottom:4px; font-size:14px;'><b>{zone}</b>: {min(occupied, cap)} / {cap} spaces{status_tag}</p>", unsafe_allow_html=True)
            st.progress(pct)
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<h4 style='font-size:15px; font-weight:600; margin-bottom:5px;'>📋 Active System Audit Stream</h4>", unsafe_allow_html=True)
        st.dataframe(st.session_state.reservations, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MODERN VIEW 2: CLIENT MOBILE INTERFACE
# ==========================================
else:
    st.markdown("<div style='text-align:center; padding: 20px 0;'><h2 style='color:#DD1B22; font-weight:700; margin-bottom:0;'>📱 PARK+ USER UTILITY</h2><p style='color:#7F8C8D; font-size:12px;'>MOBILE INTERFACE WRAPPER</p></div>", unsafe_allow_html=True)
    
    _, mock_phone, _ = st.columns([1, 1.5, 1])
    
    with mock_phone:
        if not st.session_state.logged_in:
            st.markdown("""
                <div style='background:#1A1F2C; padding:25px; border-radius:16px; border: 1px solid rgba(221,27,34,0.3); text-align:center;'>
                    <h3 style='color:#DD1B22; margin-top:0;'>Device Locked</h3>
                    <p style='color:#BDC3C7; font-size:14px;'>Please fulfill your University single sign-on parameters inside the identity sidebar configuration to gain booking tokens.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("""
            ⚙️ **System Testing Sandbox Credentials:**
            * **Student Key:** `studentmail@mahindrauniversity.edu.in` (Pass: `password123`)
            * **Faculty Key:** `facultymail@mahindrauniversity.edu.in` (Pass: `faculty123`)
            """)
        else:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top:0; font-size:20px; font-weight:600; text-align:center; color:#DD1B22;'>🚗 Smart Space Allocator</h3>", unsafe_allow_html=True)
            
            if st.session_state.user_role == "Faculty Member":
                st.markdown("<div style='background:rgba(46,204,113,0.15); border: 1px solid #2ECC71; padding:12px; border-radius:8px; font-size:13px; margin-bottom:15px; color:#2ECC71;'>🎖️ <b>Faculty Priority Mode Active:</b> Exclusive frontline bays unlocked automatically.</div>", unsafe_allow_html=True)
                selectable_zones = ["Zone A", "Zone B"]
            elif st.session_state.event_mode == "Placement Drive 2026":
                st.markdown("<div style='background:rgba(231,76,60,0.15); border: 1px solid #E74C3C; padding:12px; border-radius:8px; font-size:13px; margin-bottom:15px; color:#E74C3C;'>⚠️ <b>Recruitment Event Override Active:</b> Faculty Zone A locked. Standard traffic rerouted to student complexes.</div>", unsafe_allow_html=True)
                selectable_zones = ["Zone B", "Zone C"]
            else:
                selectable_zones = ["Zone A", "Zone B", "Zone C"]

            vehicle_num = st.text_input("Vehicle License Plate", placeholder="e.g., TS07XX1234").upper()
            target_zone = st.selectbox("Target Sector Matrix Grid", selectable_zones)
            
            if st.button("Finalize Spot Booking"):
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
                    st.success("🎉 Slot Allocation Secured!")
                    
                    st.markdown("<hr style='border-color: #2E364A;' />", unsafe_allow_html=True)
                    st.markdown("#### 🗺️ Interactive Live Indoor Wayfinding Map")
                    st.markdown(f"<div style='background:#1A1F2C; padding:12px; border-radius:8px; border-left:4px solid #3498DB; font-size:13px; color:#EAECEE;'>📍 <b>Routing Engine Path:</b> Enter via Campus Gate 2. Continue past academic Block 3, then proceed directly to row indicators within <b>{target_zone}</b>.</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:14px; font-weight:600; text-align:center; margin-bottom:5px;'>🎫 SECURE GATE ENTRY VEHICLE PASS</p>", unsafe_allow_html=True)
                    
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={vehicle_num}_{target_zone}&color=dd1b22&bgcolor=1a1f2c"
                    st.markdown(f"<div style='text-align:center;'><img src='{qr_url}' style='border: 2px solid #2E364A; border-radius:12px; padding:10px; background:#1A1F2C;' width='140'/></div>", unsafe_allow_html=True)
                else:
                    st.error("Identification string must be populated to receive validation certificates.")
            st.markdown("</div>", unsafe_allow_html=True)
