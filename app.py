import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime

# --- STYLING & THEMING (Mahindra Red & White) ---
st.set_page_config(page_title="Park+ Mahindra University", layout="wide", page_icon="🚗")

st.markdown("""
    <style>
    .main { background-color: #F4F6F8; }
    .stButton>button {
        background-color: #DD1B22;
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover { background-color: #b8141a; color: white; }
    .sidebar .sidebar-content { background-color: #DD1B22; }
    div[data-testid="stMetricContainer"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
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

# Base capacities
ZONE_CAPACITIES = {"Zone A (Faculty)": 50, "Zone B (Students)": 300, "Zone C (Hostel)": 150}

# --- FIXED LANDING LOGIC FOR RESERVATIONS ---
if not st.session_state.reservations.empty:
    active_res = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    res_counts = active_res['Zone'].value_counts()
else:
    res_counts = pd.Series(dtype=int)

zone_occupied = {
    "Zone A (Faculty)": 42 + res_counts.get("Zone A", 0),
    "Zone B (Students)": 285 + res_counts.get("Zone B", 0),
    "Zone C (Hostel)": 150 + res_counts.get("Zone C", 0)  # Hard-filled to trigger alerts
}

# --- DYNAMIC ZONE ALLOCATION LOGIC ---
if st.session_state.dynamic_switch and zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"]:
    zone_status_c = "⚠️ FULL - Spilling over to Zone B"
else:
    zone_status_c = "Full" if zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"] else "Available"

total_available = sum(max(0, ZONE_CAPACITIES[z] - zone_occupied[z]) for z in ZONE_CAPACITIES)
total_occupied = sum(min(ZONE_CAPACITIES[z], zone_occupied[z]) for z in ZONE_CAPACITIES)

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h1 style='color: #DD1B22; margin-bottom:0;'>Park+</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray; font-size:12px;'>Mahindra University Campus System</p>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("### 🔐 User Authentication")
    if not st.session_state.logged_in:
        st.session_state.user_id = st.text_input("University Email ID", placeholder="name@mahindrauniversity.edu.in")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        st.session_state.user_role = st.selectbox("Identify Your Role", ["Student", "Faculty Member", "Admin / Security"])
        if st.button("Log In"):
            if st.session_state.user_id and password:
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success(f"Logged in as: **{st.session_state.user_role}**")
        st.caption(st.session_state.user_id)
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    st.write("---")
    if st.session_state.logged_in and st.session_state.user_role == "Admin / Security":
        app_mode = st.radio("Navigate Workspace", ["🖥️ Admin Dashboard & AI Control", "📱 Mobile App View"])
    else:
        app_mode = "📱 Mobile App View"

# ==========================================
# VIEW 1: ADMIN DASHBOARD
# ==========================================
if app_mode == "🖥️ Admin Dashboard & AI Control":
    st.title("🖥️ MU Parking Command Center")
    st.write("Campus situational awareness panel powered by predictive systems.")
    
    st.subheader("🔔 Real-time System Notifications & Alerts")
    if zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"]:
        if st.session_state.dynamic_switch:
            st.warning("🔄 **Dynamic Zone Allocation Active:** Zone C has reached maximum threshold. Automatically rerouting traffic to Zone B.")
        else:
            st.error("🚨 **Critical Alert:** Zone C is completely full. System overflow warning.")
            
    if st.session_state.event_mode == "Placement Drive 2026":
        st.info("📅 **Event Mode Override Active:** Zone A reserved for corporate recruiters and guests.")

    col_dash_left, col_dash_right = st.columns([2, 1])

    with col_dash_left:
        st.write("---")
        st.subheader("📊 Live Capacity Metrics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dynamic Available Slots", total_available)
        c2.metric("Active Occupied Slots", total_occupied)
        c3.metric("Global System Cap", sum(ZONE_CAPACITIES.values()))

        st.write("---")
        st.subheader("⚙️ AI Infrastructure Rule Engines")
        col_rule1, col_rule2 = st.columns(2)
        with col_rule1:
            st.session_state.dynamic_switch = st.toggle("Enable Dynamic Zone Allocation Spillover", value=st.session_state.dynamic_switch)
        with col_rule2:
            st.session_state.event_mode = st.selectbox("Set System Event Override Status", ["Standard Operations", "Placement Drive 2026", "Annual Tech Fest"])

        st.write("---")
        st.subheader("📈 ML Demand Forecasts (Next 12 Hours)")
        chart_data = pd.DataFrame(
            np.random.randint(65, 98, size=(12, 2)),
            columns=['Predicted Load %', 'Historical Base Avg %'],
            index=[f"{i}:00" for i in range(9, 21)]
        )
        st.line_chart(chart_data)

    with col_dash_right:
        st.write("---")
        st.subheader("🗺️ Zone Space Allocations")
        for zone, cap in ZONE_CAPACITIES.items():
            occupied = zone_occupied[zone]
            pct = min(1.0, occupied / cap)
            st.markdown(f"**{zone}:** {min(occupied, cap)}/{cap} Slots")
            st.progress(pct)

        st.write("---")
        st.subheader("📋 Active Master Audit Trail")
        st.dataframe(st.session_state.reservations, use_container_width=True)

# ==========================================
# VIEW 2: MOBILE USER APP
# ==========================================
else:
    st.markdown("<h2 style='text-align: center; color: #DD1B22;'>📱 Park+ Mobile App</h2>", unsafe_allow_html=True)
    _, mock_phone, _ = st.columns([1, 1.8, 1])
    
    with mock_phone:
        if not st.session_state.logged_in:
            st.warning("🔒 Authentication Needed. Please complete your user credentials in the sidebar panel to unlock mobile flows.")
        else:
            st.markdown(f"""
                <div style='border: 1px solid #E5E7EB; padding: 15px; border-radius: 12px; background-color: white; margin-bottom: 15px;'>
                    <span style='font-size:12px; color:gray;'>Welcome Back</span>
                    <h4 style='margin:0; color:#DD1B22;'>{st.session_state.user_id.split('@')[0]}</h4>
                    <p style='margin:0; font-size:13px; font-weight:600;'>Profile Classification: {st.session_state.user_role}</p>
                </div>
            """, unsafe_allow_html=True)

            st.write("### 🚗 Smart Slot Reservation")
            
            if st.session_state.user_role == "Faculty Member":
                st.info("🎖️ **Faculty Prioritization Rules Applied:** Premium near-building rows are unlocked for your profile.")
                selectable_zones = ["Zone A", "Zone B"]
            elif st.session_state.event_mode == "Placement Drive 2026":
                st.warning("🚨 Zone A is temporarily locked for university recruitment drives. Users are routed to Zone B.")
                selectable_zones = ["Zone B", "Zone C"]
            else:
                selectable_zones = ["Zone A", "Zone B", "Zone C"]

            vehicle_num = st.text_input("Enter Registered Vehicle Plate", placeholder="e.g., TS07XX1234").upper()
            target_zone = st.selectbox("Choose Targeted Sector Grid", selectable_zones)
            
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
                    st.success("🎉 Slot Secured Successfully!")
                    
                    st.write("---")
                    st.markdown("### 🗺️ Indoor Turn-by-Turn Wayfinding")
                    st.info(f"📍 **Routing Instruction:** Enter via Main Gate 2. Proceed straight past Block 3, then follow arrows directly into the assigned row in **{target_zone}**.")
                    
                    st.markdown("---")
                    st.markdown("#### 🎫 Digital Verification Access Pass")
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={vehicle_num}_{target_zone}", width=140)
                else:
                    st.error("A vehicle number is required to generate your parking pass.")
