import streamlit as st
import random
import time
import hashlib
from datetime import datetime
import qrcode
from PIL import Image
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Smart Campus Parking System",
    page_icon="🚗",
    layout="wide"
)

# ---------------- CLEAN UI ----------------
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

# ---------------- SESSION STATE ----------------
if "active_pass" not in st.session_state:
    st.session_state.active_pass = None

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

if "event_mode" not in st.session_state:
    st.session_state.event_mode = False

# ---------------- CORE ENGINE ----------------
TOTAL_SLOTS = 500

def occupancy_model(hour, event=False):
    base = 180
    curve = (hour - 8) * 28
    event_boost = 1.35 if event else 1.0
    noise = random.randint(-8, 8)

    return int((base + curve + noise) * event_boost)

def zone_scores():
    return {
        "Zone A": random.randint(60, 95),
        "Zone B": random.randint(40, 90),
        "Zone C": random.randint(30, 85),
        "Zone D": random.randint(20, 70),
    }

zones = zone_scores()

# ---------------- NAV ----------------
st.sidebar.title("🅿️ Smart Parking System")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "AI Engine", "Live Zones", "Smart Booking", "My Pass"]
)

st.sidebar.toggle("Event Mode", key="event_mode")

# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("🏢 Campus Parking Control Center")

    hour = datetime.now().hour
    predicted = occupancy_model(hour, st.session_state.event_mode)

    occupied = min(predicted, TOTAL_SLOTS)
    available = TOTAL_SLOTS - occupied

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Capacity", TOTAL_SLOTS)
    col2.metric("Occupied", occupied)
    col3.metric("Available", available)
    col4.metric("Occupancy %", f"{round((occupied/TOTAL_SLOTS)*100,2)}%")

    st.divider()

    st.info(f"Peak Zone: {max(zones, key=zones.get)}")
    st.success(f"Best Arrival Time: {random.randint(8,10)}:{random.choice(['00','30'])} AM")

# ---------------- AI ENGINE ----------------
elif page == "AI Engine":

    st.title("🧠 Predictive AI Engine")

    hour = st.slider("Select Hour", 8, 20, 10)

    predicted = occupancy_model(hour, st.session_state.event_mode)
    risk = min(100, predicted // 5)

    st.metric("Predicted Occupancy", predicted)

    if risk > 75:
        st.error("HIGH CONGESTION")
    elif risk > 45:
        st.warning("MODERATE CONGESTION")
    else:
        st.success("LOW CONGESTION")

    best_zone = min(zones, key=zones.get)
    st.info(f"Recommended Zone → {best_zone}")

# ---------------- LIVE ZONES ----------------
elif page == "Live Zones":

    st.title("📡 Live Zone Monitoring")

    for z, v in zones.items():
        col1, col2 = st.columns([3,1])

        with col1:
            st.write(z)

        with col2:
            if v > 80:
                st.error(f"{v}% FULL")
            elif v > 50:
                st.warning(f"{v}% BUSY")
            else:
                st.success(f"{v}% FREE")

# ---------------- SMART BOOKING (REAL ENGINE) ----------------
elif page == "Smart Booking":

    st.title("🚗 Smart Parking Booking System")

    vehicle = st.text_input("Vehicle Number")
    user_type = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])

    st.info("AI automatically allocates best available slot")

    recommended_zone = min(zones, key=zones.get)

    if st.button("Generate Parking Pass"):

        if not vehicle:
            st.error("Enter vehicle number")
        else:

            with st.spinner("Allocating optimal slot..."):
                time.sleep(1.5)

            slot_available = random.choice([True, True, False])

            if slot_available:

                raw = f"{vehicle}-{datetime.now()}"
                pass_id = "PASS-" + hashlib.sha256(raw.encode()).hexdigest()[:10].upper()

                qr_data = f"""
PASS ID: {pass_id}
VEHICLE: {vehicle}
USER: {user_type}
ZONE: {recommended_zone}
TIME: {datetime.now()}
"""

                qr = qrcode.make(qr_data)
                buf = BytesIO()
                qr.save(buf)
                buf.seek(0)

                st.success("BOOKING CONFIRMED")

                st.image(buf, caption="QR PASS")

                st.code(pass_id)

                st.session_state.active_pass = pass_id

                st.session_state.bookings.append(pass_id)

                st.balloons()

            else:
                wl = "WL-" + str(random.randint(1000,9999))
                st.warning("No slots available → Waitlisted")
                st.code(wl)
                st.session_state.waitlist.append(wl)

# ---------------- MY PASS ----------------
elif page == "My Pass":

    st.title("🎫 Active Parking Pass")

    if st.session_state.active_pass:
        st.success("Active Pass Found")
        st.code(st.session_state.active_pass)

        if st.button("Cancel Pass"):
            st.session_state.active_pass = None
            st.warning("Pass Cancelled")
    else:
        st.info("No active parking pass")