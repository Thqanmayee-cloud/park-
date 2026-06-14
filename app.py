import streamlit as st
import random
import hashlib
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Smart Campus Parking System",
    page_icon="🚗",
    layout="wide"
)

# ---------------- SAFE UI ----------------
st.markdown("""
<style>
.main { background-color: #0b1220; color: #e5e7eb; }

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

div[data-testid="metric-container"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #1f2937;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}

h1, h2, h3 { color: #60a5fa; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE SAFETY ----------------
if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

if "event_mode" not in st.session_state:
    st.session_state.event_mode = False

# ---------------- CORE ENGINE ----------------
TOTAL = 500

def ai_occupancy(hour, event=False):
    base = 180
    curve = (hour - 8) * 30
    noise = random.randint(-5, 5)
    multiplier = 1.35 if event else 1.0
    return int((base + curve + noise) * multiplier)

def zone_engine():
    return {
        "Zone A (Faculty)": random.randint(60, 95),
        "Zone B (Students)": random.randint(40, 90),
        "Zone C (Hostel)": random.randint(30, 85),
        "Zone D (Visitors)": random.randint(20, 70),
    }

zones = zone_engine()

# ---------------- NAVIGATION ----------------
st.sidebar.title("🚗 Parking AI System")

page = st.sidebar.radio(
    "Menu",
    ["Dashboard", "AI Engine", "Live Zones", "Smart Booking", "My Pass"]
)

event_toggle = st.sidebar.toggle("🎯 Event Mode")
st.session_state.event_mode = event_toggle

# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("🏢 Campus Control Dashboard")

    hour = 10
    predicted = ai_occupancy(hour, st.session_state.event_mode)

    occupied = min(predicted, TOTAL)
    available = TOTAL - occupied
    rate = round((occupied / TOTAL) * 100, 2)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Slots", TOTAL)
    col2.metric("Occupied", occupied)
    col3.metric("Available", available)
    col4.metric("Occupancy %", f"{rate}%")

    st.divider()

    st.info(f"📍 Peak Zone: {max(zones, key=zones.get)}")
    st.success(f"🕒 Best Arrival Time: {random.randint(8,10)}:{random.choice(['00','30'])} AM")

# ---------------- AI ENGINE ----------------
elif page == "AI Engine":

    st.title("🧠 AI Prediction Engine")

    hour = st.slider("Select Hour", 8, 20, 10)

    predicted = ai_occupancy(hour, st.session_state.event_mode)
    risk = min(100, predicted // 5)

    st.metric("Predicted Occupancy", predicted)

    if risk > 75:
        st.error("🔴 High Congestion")
    elif risk > 45:
        st.warning("🟡 Medium Congestion")
    else:
        st.success("🟢 Low Congestion")

    best_zone = min(zones, key=zones.get)
    st.info(f"🤖 Recommended Zone → {best_zone}")

# ---------------- LIVE ZONES ----------------
elif page == "Live Zones":

    st.title("📡 Live Parking Zones")

    for z, v in zones.items():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(z)

        with col2:
            if v > 80:
                st.error(f"{v}% FULL")
            elif v > 50:
                st.warning(f"{v}% BUSY")
            else:
                st.success(f"{v}% FREE")

# ---------------- SMART BOOKING (FIXED) ----------------
elif page == "Smart Booking":

    st.title("🚗 Smart Parking Booking")

    vehicle = st.text_input("Vehicle Number")
    user_type = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])

    recommended_zone = min(zones, key=zones.get)

    st.info(f"🤖 AI Recommended Zone: {recommended_zone}")

    if st.button("Generate Parking Pass"):

        if vehicle.strip() == "":
            st.error("Please enter vehicle number")

        else:
            slot_available = random.choice([True, True, False])

            if slot_available:

                raw = f"{vehicle}-{datetime.now()}"
                pass_id = "PASS-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

                qr_text = f"""
SMART PARK PASS
ID: {pass_id}
VEHICLE: {vehicle}
USER: {user_type}
ZONE: {recommended_zone}
TIME: {datetime.now().strftime('%H:%M:%S')}
"""

                st.success("✅ Booking Confirmed")

                st.code(pass_id)
                st.text_area("📱 QR Data (Scan Simulation)", qr_text, height=150)

                st.session_state.pass_id = pass_id
                st.session_state.bookings.append(pass_id)

            else:
                wl = "WL-" + str(random.randint(1000,9999))
                st.warning("⚠ No slots available")
                st.code(wl)
                st.session_state.waitlist.append(wl)

# ---------------- MY PASS ----------------
elif page == "My Pass":

    st.title("🎫 My Parking Pass")

    if st.session_state.pass_id:
        st.success("Active Pass Available")
        st.code(st.session_state.pass_id)

        if st.button("Cancel Pass"):
            st.session_state.pass_id = None
            st.warning("Pass Cancelled")
    else:
        st.info("No active pass")