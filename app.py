import streamlit as st
import random
import time
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Campus Parking AI",
    page_icon="🚗",
    layout="wide"
)

# ---------------- CUSTOM UI STYLE ----------------
st.markdown("""
<style>

.main {
    background-color: #0e1117;
    color: white;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background-color: #1c1f26;
    border-radius: 14px;
    padding: 15px;
    box-shadow: 0px 0px 10px rgba(0,198,255,0.15);
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #00C6FF, #0072FF);
    color: white;
    border-radius: 10px;
    padding: 0.6em 1em;
    transition: 0.3s;
    font-weight: bold;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px #00C6FF;
}

/* Titles */
h1, h2, h3 {
    color: #00C6FF;
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

# ---------------- HEADER ----------------
st.title("🚗 Smart Campus Parking Intelligence System")
st.caption("Mahindra University • AI-Based Parking Optimization Prototype")

# ---------------- SIMULATED DATA ENGINE ----------------
total_slots = 500
base_occupied = random.randint(280, 420)

# event impact modifier
event_multiplier = 1.3 if st.session_state.event_mode else 1.0

occupied_slots = min(int(base_occupied * event_multiplier), total_slots)
available_slots = total_slots - occupied_slots

faculty_reserved = random.randint(40, 80)
visitor_slots = random.randint(20, 70)

occupancy_rate = round((occupied_slots / total_slots) * 100, 2)

# ---------------- DASHBOARD ----------------
st.header("🏠 Control Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Slots", total_slots)
col2.metric("Available", available_slots)
col3.metric("Occupied", occupied_slots)
col4.metric("Faculty Reserved", faculty_reserved)
col5.metric("Visitors", visitor_slots)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Occupancy %", f"{occupancy_rate}%")

with col2:
    peak_zone = random.choice(["Zone A", "Zone B", "Zone C", "Zone D"])
    st.metric("Peak Zone", peak_zone)

with col3:
    time_saved = random.randint(8, 25)
    st.metric("Avg Time Saved", f"{time_saved} min")

# ---------------- EVENT MODE ----------------
st.subheader("🎯 Event Control Mode")

event_toggle = st.toggle("Enable Event Mode (Sports / Fest / Exam)")

if event_toggle:
    st.session_state.event_mode = True
    st.warning("⚠ Event Mode ACTIVE - Demand Increased")
else:
    st.session_state.event_mode = False
    st.success("Normal Campus Mode")

# ---------------- AI ENGINE ----------------
st.header("🤖 AI Prediction Engine")

hour = st.slider("Select Time of Day", 8, 20, 10)

trend = (hour - 8) * 32
noise = random.randint(-15, 15)

predicted = int(180 + trend + noise)

if st.session_state.event_mode:
    predicted = int(predicted * 1.4)

st.progress(min(int(predicted / 5), 100))

st.metric("Predicted Occupancy", predicted)

risk = min(100, predicted // 5)

if risk > 75:
    st.error("🔴 HIGH CONGESTION WARNING")
elif risk > 45:
    st.warning("🟡 MODERATE TRAFFIC")
else:
    st.success("🟢 SMOOTH FLOW")

# Smart recommendations
zone_reco = random.choice(["Zone B (Students)", "Zone C (Hostel)", "Zone D (Visitors)"])
st.info(f"📍 Smart Recommendation: Use {zone_reco}")

best_time = f"{random.randint(8,10)}:{random.choice(['00','30'])} AM"
st.success(f"🕒 Best Arrival Time: {best_time}")

# Exam prediction
exam_risk = random.randint(60, 95)
st.metric("📚 Exam Day Risk Index", f"{exam_risk}%")

# Event impact
event_impact = random.randint(30, 90) if st.session_state.event_mode else random.randint(10, 40)
st.metric("🎉 Event Impact Score", f"{event_impact}%")

# ---------------- LIVE ZONES ----------------
st.header("📡 Live Parking Zones")

zones = {
    "Zone A (Faculty)": random.randint(60, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Hostel)": random.randint(30, 85),
    "Zone D (Visitors)": random.randint(20, 70),
}

for z, val in zones.items():
    if val > 80:
        st.error(f"{z} → {val}% FULL 🔴")
    elif val > 50:
        st.warning(f"{z} → {val}% BUSY 🟡")
    else:
        st.success(f"{z} → {val}% FREE 🟢")

# ---------------- RESERVATION SYSTEM ----------------
st.header("🎟 Smart Reservation System")

step = st.radio("Reservation Step", ["Vehicle", "User Type", "Zone", "Time", "Confirm"])

if step == "Vehicle":
    vehicle = st.text_input("Enter Vehicle Number")

elif step == "User Type":
    user_type = st.selectbox("Select Type", ["Student", "Faculty", "Visitor"])

elif step == "Zone":
    zone = st.selectbox("Select Zone", ["A", "B", "C", "D"])

elif step == "Time":
    time_slot = st.selectbox("Select Slot", ["8-10", "10-12", "12-2", "2-4", "4-6"])

elif step == "Confirm":

    if st.button("Generate Smart Parking Pass"):

        with st.spinner("Generating QR Pass..."):
            time.sleep(2)

        slot_available = random.choice([True, False])

        if slot_available:
            pass_id = f"MU-{random.randint(1000,9999)}"
            st.success("✅ Reservation Confirmed")
            st.code(pass_id)
            st.balloons()

            st.session_state.reservations.append(pass_id)

        else:
            st.warning("⚠ No slots available - Added to Waitlist")
            wait_id = f"WL-{random.randint(1000,9999)}"
            st.info(wait_id)
            st.session_state.waitlist.append(wait_id)

# ---------------- HISTORY ----------------
st.header("📊 System Logs")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Confirmed Reservations")
    st.write(st.session_state.reservations if st.session_state.reservations else "No data yet")

with col2:
    st.subheader("Waitlist Queue")
    st.write(st.session_state.waitlist if st.session_state.waitlist else "No data yet")

# ---------------- FOOTER ----------------
st.divider()
st.caption("🚗 Smart Campus Parking AI System • Prototype v2.0 • Mahindra University")
