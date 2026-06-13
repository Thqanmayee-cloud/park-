import streamlit as st
import pandas as pd
import numpy as np
import time

# --- STYLING & THEMING (Mahindra Red & White) ---
st.set_page_config(page_title="Park+ Mahindra University", layout="wide", page_icon="🚗")

# Custom CSS to inject the Mahindra Red (#DD1B22) brand identity
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
    .metric-label { color: #6B7280; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE (To keep data persistent) ---
if 'reservations' not in st.session_state:
    st.session_state.reservations = pd.DataFrame(columns=['Vehicle Number', 'Zone', 'Timestamp'])
if 'available_slots' not in st.session_state:
    st.session_state.available_slots = 120
if 'occupied_slots' not in st.session_state:
    st.session_state.occupied_slots = 380

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h1 style='color: #DD1B22;'>Park+</h1>", unsafe_allow_html=True)
    st.markdown("### Mahindra University")
    st.write("---")
    app_mode = st.radio("Select View Mode", ["🖥️ Admin Command Center", "📱 Mobile User App"])

# ==========================================
# MODE 1: ADMIN COMMAND CENTER
# ==========================================
if app_mode == "🖥️ Admin Command Center":
    st.title("🖥️ MU Parking Command Center")
    st.write("Real-time campus situational awareness panel.")
    
    # 1. NOTIFICATIONS & ALERTS PANEL
    st.subheader("🔔 Live System Notifications")
    if st.session_state.available_slots < 120:
        st.success(f"✅ Slot successfully allocated dynamically in Zone A for recent vehicle.")
    st.error("⚠️ Alert: Zone C (Hostel) is currently at 100% capacity. Dynamic re-routing active.")
    
    st.write("---")
    
    # 2. METRICS / STATS CARDS
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Available Slots", value=st.session_state.available_slots, delta="Live data")
    with col2:
        st.metric(label="Occupied Slots", value=st.session_state.occupied_slots)
    with col3:
        st.metric(label="Total Capacity", value=500)
        
    st.write("---")

    # 3. LIVE CAMPUS PARKING PARKING MAP (Interactive Simulation)
    st.subheader("🗺️ Live Campus Parking Allocation Map")
    
    # Simulating coordinates roughly around the campus area
    map_data = pd.DataFrame({
        'lat': [17.5350, 17.5355, 17.5360],
        'lon': [78.3810, 78.3815, 78.3820],
        'Zone': ['Zone A (Faculty)', 'Zone B (Students)', 'Zone C (Hostel)'],
        'Status': ['Available', 'Limited', 'Full']
    })
    
    col_map, col_legend = st.columns([3, 1])
    with col_map:
        st.map(map_data, latitude='lat', longitude='lon', zoom=15)
    with col_legend:
        st.markdown("### Dynamic Zone Status")
        st.markdown("🟢 **Zone A (Faculty):** Available")
        st.markdown("🟡 **Zone B (Students):** Limited")
        st.markdown("🔴 **Zone C (Hostel):** Full")
        
    # 4. RECENT RESERVATIONS DATA TABLE
    st.write("---")
    st.subheader("📋 Active Reservation Ledger")
    if st.session_state.reservations.empty:
        st.info("No active custom mobile reservations recorded yet.")
    else:
        st.dataframe(st.session_state.reservations, use_container_width=True)

# ==========================================
# MODE 2: MOBILE USER APP
# ==========================================
else:
    st.markdown("<h2 style='text-align: center; color: #DD1B22;'>📱 Park+ Mobile App</h2>", unsafe_allow_html=True)
    
    _, mock_phone, _ = st.columns([1, 2, 1])
    
    with mock_phone:
        st.markdown("""
            <div style='border: 2px solid #E5E7EB; padding: 20px; border-radius: 20px; background-color: white;'>
                <h4 style='color:#DD1B22; text-align:center;'>Mahindra University Login</h4>
                <p style='text-align:center; font-size:12px; color:gray;'>Authenticated Session: Student / Faculty</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.write("### 🚗 Reserve Your Space")
        
        vehicle_num = st.text_input("Enter Vehicle Number", placeholder="e.g., TS07XX1234")
        selected_zone = st.selectbox("Select Desired Zone", ["Zone A (Faculty Priority)", "Zone B (Student Core)", "Zone C (Hostel)"])
        
        if st.button("Confirm Slot Reservation"):
            if vehicle_num:
                new_res = pd.DataFrame([{
                    'Vehicle Number': vehicle_num,
                    'Zone': selected_zone,
                    'Timestamp': time.strftime("%H:%M:%S")
                }])
                st.session_state.reservations = pd.concat([st.session_state.reservations, new_res], ignore_index=True)
                
                st.session_state.available_slots -= 1
                st.session_state.occupied_slots += 1
                
                st.balloons()
                st.success(f"🎉 Success! Slot dynamically locked in {selected_zone}.")
                
                st.markdown("---")
                st.markdown("#### 🎫 Digital Parking Gate Pass")
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + vehicle_num, width=150, caption="Scan at MU Gate Entrance")
            else:
                st.warning("Please enter a valid vehicle number to request allocation.")
