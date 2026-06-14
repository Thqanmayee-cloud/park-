import streamlit as st
import random

st.set_page_config(
    page_title="Smart Campus Parking System",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Smart Campus Parking Management System")
st.markdown("### Mahindra University - AI Based Parking Prototype")

# -----------------------------
# DATA SIMULATION
# -----------------------------
total_slots = 500
occupied_slots = random.randint(280, 420)
faculty_reserved = random.randint(40, 80)
visitor_slots = random.randint(30, 80)

available_slots = total_slots - occupied_slots
occupancy_rate = round((occupied_slots / total_slots) * 100, 2)

# -----------------------------
# DASHBOARD KPIs
# -----------------------------
st.header("🏠 Dashboard Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Slots", total_slots)
col2.metric("Available Slots", available_slots)
col3.metric("Occupied Slots", occupied_slots)
col4.metric("Faculty Reserved", faculty_reserved)
col5.metric("Visitor Slots", visitor_slots)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Occupancy Rate %", f"{occupancy_rate}%")

with col2:
    peak_zone = random.choice(["Zone A", "Zone B", "Zone C", "Zone D"])
    st.metric("Peak Zone", peak_zone)

with col3:
    time_saved = random.randint(8, 25)
    st.metric("Avg Search Time Saved", f"{time_saved} min")

# -----------------------------
# AI PREDICTION ENGINE
# -----------------------------
st.divider()
st.header("🤖 AI Prediction Engine")

hour = st.slider("Select Hour of Day", 8, 20, 10)

predicted_occupancy = int(200 + (hour - 8) * 28 + random.randint(-20, 20))

st.metric("Predicted Occupancy", predicted_occupancy)

# simple risk score
risk_score = min(100, int(predicted_occupancy / 5))

st.metric("Congestion Risk Score", f"{risk_score}/100")

if risk_score > 70:
    st.error("🚨 High congestion expected during this time")
elif risk_score > 40:
    st.warning("⚠ Moderate congestion expected")
else:
    st.success("✅ Low congestion expected")

# Best arrival time
best_time = f"{random.randint(8, 10)}:{random.choice(['00','30'])} AM"
st.info(f"🕒 Best Arrival Time: {best_time}")

# Smart zone suggestion
smart_zone = random.choice([
    "Zone B - Students",
    "Zone C - Hostel",
    "Zone D - Visitors"
])
st.success(f"📍 Recommended Parking Zone: {smart_zone}")

# Exam day prediction
exam_day = random.randint(60, 95)
st.metric("Exam Day Congestion Forecast", f"{exam_day}%")

if exam_day > 80:
    st.error("📚 Exam Day Alert: Severe congestion expected")

# Event impact
event_impact = random.randint(20, 85)
st.metric("Event Impact Score", f"{event_impact}%")

if event_impact > 60:
    st.warning("🎉 Campus event causing high parking load")

# -----------------------------
# SMART RESERVATION SYSTEM
# -----------------------------
st.divider()
st.header("🎟 Smart Reservation System")

vehicle = st.text_input("Vehicle Number")

user_type = st.selectbox(
    "User Type",
    ["Student", "Faculty", "Visitor"]
)

zone = st.selectbox(
    "Zone Preference",
    ["Zone A - Faculty", "Zone B - Students", "Zone C - Hostel", "Zone D - Visitors"]
)

time_slot = st.selectbox(
    "Time Slot",
    ["8-10 AM", "10-12 PM", "12-2 PM", "2-4 PM", "4-6 PM"]
)

# simulate availability
slot_available = random.choice([True, False])

if st.button("Reserve Parking"):

    if vehicle.strip() == "":
        st.error("⚠ Please enter vehicle number")

    elif slot_available:
        st.success("✅ Reservation Confirmed")

        qr_code = f"MU-PASS-{random.randint(1000,9999)}"
        st.code(qr_code)

        st.info("🎫 QR Pass Generated (Simulated)")

    else:
        st.warning("⚠ Selected zone is full")
        st.info("📌 Added to WAITLIST. You will be notified when slot opens.")

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.caption("Smart Campus Parking System - Prototype for Mahindra University")
