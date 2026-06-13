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
    .alert-box {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM STATE ENGINE (To power advanced features) ---
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

# Base zone capacities
ZONE_CAPACITIES = {"Zone A (Faculty)": 50, "Zone B (Students)": 300, "Zone C (Hostel)": 150}

# Calculate current dynamic capacities based on simulated live load and active reservations
res_counts = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']['Zone'].value_counts()
zone_occupied = {
    "Zone A (Faculty)": 42 + res_counts.get("Zone A (Faculty)", 0),
    "Zone B (Students)": 285 + res_counts.get("Zone B (Students)", 0),
    "Zone C (Hostel)": 150 + res_counts.get("Zone C (Hostel)", 0) # Hard-filled to trigger alerts
}

# --- DYNAMIC ZONE ALLOCATION LOGIC ---
if st.session_state.dynamic_switch and zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"]:
    # Automatically overflow Hostel spillover into Student Core (Zone B)
    zone_status_c = "⚠️ FULL - Spilling over to Zone B"
else:
    zone_status_c = "Full" if zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"] else "Available"

total_available = sum(max(0, ZONE_CAPACITIES[z] - zone_occupied[z]) for z in ZONE_CAPACITIES)
total_occupied = sum(min(ZONE_CAPACITIES[z], zone_occupied[z]) for z in ZONE_CAPACITIES)

# --- SIDEBAR INTERFACE CONTROLLER ---
with st.sidebar:
    st.markdown(f"<h1 style='color: #DD1B22; margin-bottom:0;'>Park+</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray; font-size:12px;'>Mahindra University Smart Campus</p>", unsafe_allow_html=True)
    st.write("---")
    
    # 1. USER LOGIN / AUTHENTICATION STATE SHIFTER
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
    # Route view access based on system context
    if st.session_state.logged_in and st.session_state.user_role == "Admin / Security":
        app_mode = st.radio("Navigate Workspace", ["🖥️ Admin Dashboard & AI Control", "📱 Mobile App View"])
    else:
        app_mode = "📱 Mobile App View"

# ==========================================
# FEATURE GROUP A: ADMIN DASHBOARD & AI CONTROL
# ==========================================
if app_mode == "🖥️ Admin Dashboard & AI Control":
    st.title("🖥️ MU Parking Command Center")
    st.write("Campus situational awareness system backed by predictive optimization engines.")
    
    # 5. NOTIFICATIONS AND ALERTS
    st.subheader("🔔 Real-time System Notifications & Alerts")
    if zone_occupied["Zone C (Hostel)"] >= ZONE_CAPACITIES["Zone C (Hostel)"]:
        if st.session_state.dynamic_switch:
            st.warning("🔄 **Dynamic Zone Allocation Active:** Zone C has breached safety threshold. Automatically re-routing traffic to Zone B.")
        else:
            st.error("🚨 **Critical Alert:** Zone C is completely full. System overflow warning.")
            
    if st.session_state.event_mode == "Placement Drive 2026":
        st.info("📅 **Event Mode Override Active:** Zone A reserved for corporate recruiters and VIP transit vehicles.")

    col_dash_left, col_dash_right = st.columns([2, 1])

    with col_dash_left:
        # 2. SHOWING PARKING AVAILABILITY
        st.write("---")
        st.subheader("📊 Live Capacity Metrics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dynamic Available Slots", total_available, delta="-3 from last hour")
        c2.metric("Active Occupied Slots", total_occupied, delta="+12 vs yesterday")
        c3.metric("Global System Cap", sum(ZONE_CAPACITIES.values()))

        # 4. DYNAMIC ZONE ALLOCATION & 3. EVENT PARKING MANAGEMENT CONTROL PANEL
        st.write("---")
        st.subheader("⚙️ AI Infrastructure Rule Engines")
        
        col_rule1, col_rule2 = st.columns(2)
        with col_rule1:
            st.session_state.dynamic_switch = st.toggle("Enable Dynamic Zone Allocation Spillover", value=st.session_state.dynamic_switch)
            st.caption("Automatically opens adjacent zones when a high-density target sector overflows.")
        with col_rule2:
            st.session_state.event_mode = st.selectbox("Set System Event Override Status", ["Standard Operations", "Placement Drive 2026", "Annual Tech Fest / Convocation"])
            st.caption("Alters baseline routing metrics and priorities across the grid map.")

        # 1. DEMAND PREDICTIONS GRAPHING
        st.write("---")
        st.subheader("📈 ML Demand Forecasts (Next 12 Hours)")
        chart_data = pd.DataFrame(
            np.random.randint(65, 98, size=(12, 2)),
            columns=['Predicted Load %', 'Historical Base Avg %'],
            index=[f"{i}:00" for i in range(9, 21)]
        )
        st.line_chart(chart_data)
        st.caption("🔮 **AI Prediction Warning:** High risk spike identified between 10:00 AM - 12:15 PM due to conflicting lecture slots.")

    with col_dash_right:
        st.write("---")
        st.subheader("🗺️ Zone Space Allocations")
        
        st.markdown(f"**Zone A (Faculty Only):** {zone_occupied['Zone A (Faculty)']}/{ZONE_CAPACITIES['Zone A (Faculty)']} Slots")
        st.progress(zone_occupied['Zone A (Faculty)'] / ZONE_CAPACITIES['Zone A (Faculty)'])
        
        st.markdown(f"**Zone B (Student Core):** {zone_occupied['Zone B (Students)']}/{ZONE_CAPACITIES['Zone B (Students)']} Slots")
        st.progress(zone_occupied['Zone B (Students)'] / ZONE_CAPACITIES['Zone B (Students)'])
        
        st.markdown(f"**Zone C (Hostel Block):** {zone_occupied['Zone C (Hostel)']}/{ZONE_CAPACITIES['Zone C (Hostel)']} ({zone_status_c})")
        st.progress(min(1.0, zone_occupied['Zone C (Hostel)'] / ZONE_CAPACITIES['Zone C (Hostel)']))

        st.write("---")
        st.subheader("📋 Active Master Audit Trail")
        st.dataframe(st.session_state.reservations, use_container_width=True)

# ==========================================
# FEATURE GROUP B: MOBILE USER APPLICATION FLOW
# ==========================================
else:
    st.markdown("<h2 style='text-align: center; color: #DD1B22;'>📱 Park+ Mobile App</h2>", unsafe_allow_html=True)
    
    _, mock_phone, _ = st.columns([1, 1.8, 1])
    
    with mock_phone:
        if not st.session_state.logged_in:
            st.warning("🔒 Authentication Needed. Please complete your user verification credentials in the sidebar panel to unlock reservation workflows.")
        else:
            st.markdown(f"""
                <div style='border: 1px solid #E5E7EB; padding: 15px; border-radius: 12px; background-color: white; margin-bottom: 15px;'>
                    <span style='font-size:12px; color:gray;'>Welcome Back</span>
                    <h4 style='margin:0; color:#DD1B22;'>{st.session_state.user_id.split('@')[0]}</h4>
                    <p style='margin:0; font-size:13px; font-weight:600;'>Account Priority Classification: {st.session_state.user_role}</p>
                </div>
            """, unsafe_allow_html=True)

            # 2. FACULTY PRIORITY ALLOCATION IN REAL-TIME BOOKING
            st.write("### 📅 Smart Slot Reservation")
            
            # Active Priority allocation rule notification display
            if st.session_state.user_role == "Faculty Member":
                st.info("🎖️ **Faculty Prioritization Rules Applied:** Premium near-building rows are completely unlocked for your reservation profile.")
                selectable_zones = ["Zone A (Faculty Priority)", "Zone B (Student Core)"]
            elif st.session_state.event_mode == "Placement Drive 2026":
                st.warning("🚨 Zone A is temporarily locked down for university recruiters. Student accounts are routed to Zone B and alternate lots.")
                selectable_zones = ["Zone B (Student Core)", "Zone C (Hostel)"]
            else:
                selectable_zones = ["Zone B (Student Core)", "Zone C (Hostel)"]

            vehicle_num = st.text_input("Enter Registered Vehicle Plate", placeholder="e.g., TS07XX1234").upper()
            target_zone = st.selectbox("Choose Targeted Sector Grid", selectable_zones)
            
            # 3. SLOT RESERVATION ACTION HANDLER
            if st.button("Finalize Spot Booking"):
                if vehicle_num:
                    clean_zone_name = target_zone.split(" (")[0]
                    
                    # Log data instantly to background frame
                    new_log = pd.DataFrame([{
                        'Vehicle Number': vehicle_num,
                        'Role': st.session_state.user_role,
                        'Zone': clean_zone_name,
                        'Timestamp': datetime.datetime.now().strftime("%I:%M %p"),
                        'Status': 'Active'
                    }])
                    st.session_state.reservations = pd.concat([st.session_state.reservations, new_log], ignore_index=True)
                    
                    st.balloons()
                    st.success("🎉 Slot Secured Successfully!")
                    
                    # 4. NAVIGATING TO THE ASSIGNED PARKING SPACE (Wayfinding logic maps)
                    st.write("---")
                    st.markdown("### 🗺️ Indoor Turn-by-Turn Wayfinding")
                    st.info(f"📍 **Routing Instruction:** Pass through Main Entry Gate 2. Continue straight, turn left at Block 3, proceed to assigned bay row in **{clean_zone_name}**.")
                    
                    # Render Pass Pass QR Code
                    st.markdown("---")
                    st.markdown("#### 🎫 Digital Verification Access Pass")
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={vehicle_num}_{clean_zone_name}", width=140, caption="Scan at entry boom barrier gate sensor")
                else:
                    st.error("A structural vehicle identification number is mandatory to secure an encrypted pass.")
