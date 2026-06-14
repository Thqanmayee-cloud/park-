import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- 1. SET UP THE BASE LAYOUT ENGINE FIRST ---
st.set_page_config(
    page_title="Park+ Elite Terminal", 
    layout="wide", 
    page_icon="⚡"
)

# --- 2. CLEAN HIGH-CONTRAST PRESENTATION THEME (STABLE BUILD) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    /* Clean CSS Reset to avoid layout bricking */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0B0F17 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #F8FAFC !important;
    }
    
    /* Sleek Title Blocks */
    .main-title {
        color: #F43F5E;
        font-weight: 800;
        font-size: 32px;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }
    
    .subtitle {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 30px;
    }

    /* Presentation Stat Boxes */
    .stat-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-top: 4px solid #F43F5E;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    /* Custom Notification Banners */
    .alert-banner {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid #F59E0B;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    
    /* Form input labels formatting */
    label {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        letter-spacing: 0.5px;
    }
    
    /* High-Visibility Custom Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #F43F5E 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 20px !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(244, 63, 94, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC DATA AND RESERVATION STORAGE ---
if 'reservations' not in st.session_state:
    st.session_state.reservations = pd.DataFrame(columns=['Vehicle Plate', 'Profile Type', 'Assigned Lot', 'Timestamp', 'Status'])

# Fixed capacity matrices for Mahindra University zones
TOTAL_CAPACITIES = {"Zone A (Faculty Only)": 50, "Zone B (General Student)": 300, "Zone C (Hostel Complex)": 150}

# Calculate current lot capacities dynamically
if not st.session_state.reservations.empty:
    active_logs = st.session_state.reservations[st.session_state.reservations['Status'] == 'Active']
    live_counts = active_logs['Assigned Lot'].value_counts()
else:
    live_counts = pd.Series(dtype=int)

# Seed metrics so the presentation looks populated from the start
current_occupied = {
    "Zone A (Faculty Only)": 44 + live_counts.get("Zone A (Faculty Only)", 0),
    "Zone B (General Student)": 282 + live_counts.get("Zone B (General Student)", 0),
    "Zone C (Hostel Complex)": 150 + live_counts.get("Zone C (Hostel Complex)", 0)
}

# Determine if overflow mechanisms need to trigger
hostel_overflow_active = current_occupied["Zone C (Hostel Complex)"] >= TOTAL_CAPACITIES["Zone C (Hostel Complex)"]
net_available = sum(max(0, TOTAL_CAPACITIES[z] - current_occupied[z]) for z in TOTAL_CAPACITIES)
net_occupied = sum(min(TOTAL_CAPACITIES[z], current_occupied[z]) for z in TOTAL_CAPACITIES)

# --- 4. HEADER BRANDING ---
st.markdown('<div class="main-title">Park+ Infrastructure Core</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Mahindra University Smart Transit Management & Analytics Terminal</div>', unsafe_allow_html=True)

# --- 5. WORKSPACE SELECTOR TOP-BAR ---
current_workspace = st.selectbox(
    "CHOOSE WORKSPACE VIEW",
    ["📱 Client Reservation App", "🔒 Admin Infrastructure Dashboard Panel"]
)

st.markdown("---")

# ==================================================================================
# VIEW 1: USER APP TERMINAL
# ==================================================================================
if current_workspace == "📱 Client Reservation App":
    
    # REQUIREMENT: Notifications
    if hostel_overflow_active:
        st.markdown("""
            <div class="alert-banner">
                <b style="color: #F59E0B;">🔄 AUTOMATED TRAFFIC OVERFLOW PROTOCOL ACTIVE</b><br>
                <span style="color: #94A3B8; font-size: 13px;">Sector C has reached max structural capacity. The routing engine is automatically distributing upcoming general student entries into alternative Zone B spaces.</span>
            </div>
        """, unsafe_allow_html=True)

    col_form, col_nav = st.columns([1, 1])
    
    with col_form:
        st.subheader("Reserve a Parking Spot")
        user_profile = st.selectbox("Identify Profile Classification", ["Student General", "Faculty Representative"])
        
        # REQUIREMENT: Zone Allocation & Priority Parking rules
        if user_profile == "Faculty Representative":
            allowed_selections = ["Zone A (Faculty Only)", "Zone B (General Student)"]
            st.info("🎖️ Faculty Priority Unlocked: Frontline proximity bays inside Zone A are available.")
        else:
            allowed_selections = ["Zone B (General Student)", "Zone C (Hostel Complex)"]
            st.caption("Standard student access permissions mapped to general campus zones.")
            
        vehicle_plate = st.text_input("Vehicle License Registration Plate", placeholder="e.g., TS07XX1234").upper()
        target_allocation = st.selectbox("Specify Target Sector Lane", allowed_selections)
