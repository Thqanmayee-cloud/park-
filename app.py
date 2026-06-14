import streamlit as st
import random
import time
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Campus Parking Management System",
    page_icon="🅿️",
    layout="wide"
)

# ---------------- PROFESSIONAL UI THEME ----------------
st.markdown("""
<style>
.main {
    background-color: #0b1220;
    color: #e6edf3;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

/* Cards */
div[data-testid="metric-container"] {
    background-color: #111c2e;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #1f2a44;
}

/* Buttons */
.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    border: none;
}

.stButton button:hover {
    background-color: #1d4ed8;
}

/* Titles */
h1, h2, h3 {
    color: #60a5fa;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "reservations" not in st.session_state:
    st.session_state.reservations = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

if "event_mode" not in st.session_state:
    st.session_state.event_mode = False

# ---------------- NAVIGATION ----------------
st.sidebar.title("🅿️ Campus Parking System")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "AI Engine", "Live Zones", "Reservation", "Logs"]
)

st.sidebar.divider()
st.sidebar.caption("Mahindra University • Smart Infrastructure Prototype")

# ---------------- BASE DATA ENGINE ----------------
TOTAL_SLOTS = 500

base_occupied = random.randint(280, 420)
event_factor = 1.35 if st.session_state.event_mode else 1.0

occupied = min(int(base_occupied * event_factor), TOTAL_SLOTS)
available = TOTAL_SLOTS - occupied

occupancy_rate = round((occupied / TOTAL_SLOTS) * 100, 2)

zones = {
    "Zone A (Faculty)": random.randint(65, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Hostel)": random.randint(30, 85),
    "Zone D (Visitors)": random.randint(20, 75),
}

# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("🏢 Campus Parking Control Center")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Capacity", TOTAL_SLOTS)
    col2.metric("Occupied", occupied)
    col3.metric("Available", available)
    col4.metric("Occupancy %", f"{occupancy_rate}%")

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Peak Zone", max(zones, key=zones.get))
    col2.metric("Avg Search Time Saved", f"{random.randint(6, 18)} min")
    col3.metric("System Load Index", f"{random.randint(40, 90)}/100")

    st.divider()

    st.subheader("🎯 Event Mode Control")

    toggle = st.toggle("Enable Event Mode (Fest / Exam / Sports)")

    st.session_state.event_mode = toggle

    if toggle:
        st.warning("Event Mode Active → Demand Surge Simulation Enabled")
    else:
        st.info("Normal Campus Operations")

# ---------------- AI ENGINE ----------------
elif page == "AI Engine":

    st.title("🧠 Predictive Analytics Engine")

    hour = st.slider("Select Time Window", 8, 20, 10)

    trend = (hour - 8) * 30
    noise = random.randint(-12, 12)

    prediction = int(190 + trend + noise)

    if st.session_state.event_mode:
        prediction = int(prediction * 1.4)

    st.metric("Predicted Occupancy", prediction)

    risk = min(100, prediction // 5)

    if risk > 75:
        st.error("High congestion predicted")
    elif risk > 45:
        st.warning("Moderate congestion predicted")
    else:
        st.success("Low congestion predicted")

    st.divider()

    st.subheader("System Recommendations")

    st.info(f"Recommended Zone: {random.choice(list(zones.keys()))}")
    st.success(f"Best Arrival Time: {random.randint(8,10)}:{random.choice(['00','30'])} AM")

    st.metric("Congestion Risk Score", f"{risk}/100")

    exam_risk = random.randint(60, 95)
    st.metric("Exam Day Load Forecast", f"{exam_risk}%")

    event_impact = random.randint(20, 85) if st.session_state.event_mode else random.randint(10, 40)
    st.metric("Event Impact Index", f"{event_impact}%")

# ---------------- LIVE ZONES ----------------
elif page == "Live Zones":

    st.title("📡 Live Parking Infrastructure")

    st.caption("Real-time simulated occupancy monitoring system")

    for zone, value in zones.items():

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(zone)

        with col2:
            if value > 80:
                st.error(f"{value}% FULL")
            elif value > 50:
                st.warning(f"{value}% BUSY")
            else:
                st.success(f"{value}% FREE")

# ---------------- RESERVATION ----------------
elif page == "Reservation":

    st.title("🎟 Smart Parking Reservation System")

    step = st.selectbox("Step", ["Vehicle", "User Type", "Zone", "Time", "Confirm"])

    if step == "Vehicle":
        vehicle = st.text_input("Vehicle Number")

    elif step == "User Type":
        user_type = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])

    elif step == "Zone":
        zone = st.selectbox("Preferred Zone", list(zones.keys()))

    elif step == "Time":
        slot = st.selectbox("Time Slot", ["8-10", "10-12", "12-2", "2-4", "4-6"])

    elif step == "Confirm":

        if st.button("Generate Parking Pass"):

            with st.spinner("Allocating optimal slot..."):
                time.sleep(1.5)

            slot_available = random.choice([True, False])

            if slot_available:
                pass_id = f"PASS-{random.randint(1000,9999)}"

                st.success("Reservation Confirmed")
                st.code(pass_id)

                st.session_state.reservations.append({
                    "id": pass_id,
                    "time": datetime.now().strftime("%H:%M:%S")
                })

                st.balloons()

            else:
                wait_id = f"WL-{random.randint(1000,9999)}"

                st.warning("No slots available")
                st.info(f"Added to Waitlist: {wait_id}")

                st.session_state.waitlist.append(wait_id)

# ---------------- LOGS ----------------
elif page == "Logs":

    st.title("📊 System Audit Logs")

    st.subheader("Confirmed Reservations")

    if st.session_state.reservations:
        for r in st.session_state.reservations[-10:]:
            st.write(f"✔ {r['id']} | {r['time']}")
    else:
        st.info("No reservations yet")

    st.subheader("Waitlist Queue")

    if st.session_state.waitlist:
        for w in st.session_state.waitlist[-10:]:
            st.write(f"⏳ {w}")
    else:
        st.info("No waitlist entries")

# ---------------- FOOTER ----------------
st.sidebar.divider()
st.sidebar.caption("System v1.0 • Smart Campus Infrastructure")
