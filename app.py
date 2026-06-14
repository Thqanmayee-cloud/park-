import streamlit as st
import random
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image

# ================= CONFIG =================
st.set_page_config(
    page_title="Park+ | Smart Campus Parking System",
    layout="wide",
    page_icon="🚗"
)

# ================= SESSION =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# ================= BASE DATA =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}

# ================= COMPUTE LIVE DATA =================
def compute_zones():
    used = {"Zone A (Faculty)": 0, "Zone B (Students)": 0, "Zone C (Visitors)": 0}

    for b in st.session_state.bookings:
        used[b["Zone"]] += 1

    available = {
        z: max(BASE_ZONES[z] - used[z], 0)
        for z in BASE_ZONES
    }

    return used, available

occupied, available = compute_zones()

TOTAL = sum(BASE_ZONES.values())
total_used = sum(occupied.values())
occupancy = round((total_used / TOTAL) * 100, 2)

# ================= AI SUGGESTION =================
def ai_zone(role):
    if role == "Faculty":
        return "Zone A (Faculty)"
    elif role == "Student":
        return "Zone B (Students)"
    return "Zone C (Visitors)"

def notify(msg):
    st.session_state.alerts.append(
        f"{datetime.now().strftime('%H:%M:%S')} - {msg}"
    )

def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# ================= STYLE =================
st.markdown("""
<style>
.main { background-color: #0b1220; color: #e5e7eb; }

.title {
    font-size: 28px;
    font-weight: 700;
    color: #60a5fa;
}

.card {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    text-align: center;
}

.stButton button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation System", "📊 Dashboard"]
)

# ======================================================
# 🗺️ MAP VIEW (CLEAN + SIMPLE)
# ======================================================
if page == "🗺️ Map View":

    st.subheader("📍 Campus Parking Map (Zone View)")

    st.info("""
    🟢 Faculty Zone → Priority Parking  
    🔵 Student Zone → Standard Parking  
    🟡 Visitor Zone → Temporary Parking  
    """)

    st.markdown("### 🧭 Live Zone Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("🟢 Faculty Zone")
        st.metric("Available", available["Zone A (Faculty)"])
        st.metric("Occupied", occupied["Zone A (Faculty)"])
        st.progress(occupied["Zone A (Faculty)"] / BASE_ZONES["Zone A (Faculty)"])

    with col2:
        st.info("🔵 Student Zone")
        st.metric("Available", available["Zone B (Students)"])
        st.metric("Occupied", occupied["Zone B (Students)"])
        st.progress(occupied["Zone B (Students)"] / BASE_ZONES["Zone B (Students)"])

    with col3:
        st.warning("🟡 Visitor Zone")
        st.metric("Available", available["Zone C (Visitors)"])
        st.metric("Occupied", occupied["Zone C (Visitors)"])
        st.progress(occupied["Zone C (Visitors)"] / BASE_ZONES["Zone C (Visitors)"])

    st.markdown("---")

    st.markdown("### 🏫 Campus Layout (Simplified Map View)")

    st.write("🟢 Faculty Parking Area → Near Admin Block")
    st.write("🔵 Student Parking Area → Main Entrance Side")
    st.write("🟡 Visitor Parking Area → Gate Entry Zone")

    st.success("💡 This is a simplified campus map view for better understanding in demos")

# ======================================================
# 🅿️ RESERVATION SYSTEM
# ======================================================
elif page == "🅿️ Reservation System":

    st.subheader("🎟 Smart Reservation Panel")

    role = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])
    vehicle = st.text_input("Vehicle Number")

    ai_suggestion = ai_zone(role)
    st.info(f"🤖 AI Suggested Zone → {ai_suggestion}")

    if st.button("Generate Parking Pass"):

        if vehicle.strip() == "":
            st.error("Enter vehicle number")

        elif available[ai_suggestion] <= 0:
            st.error("No slots available in this zone")

        else:

            pid = "PARK+" + hashlib.md5(
                (vehicle + str(datetime.now())).encode()
            ).hexdigest()[:10].upper()

            qr_data = f"""
PARK+ CAMPUS
ID: {pid}
ROLE: {role}
ZONE: {ai_suggestion}
TIME: {datetime.now()}
"""

            qr_img = make_qr(qr_data)

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Role": role,
                "Zone": ai_suggestion,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            notify(f"{role} booked {ai_suggestion}")

            st.success("Booking Confirmed 🚗")
            st.image(qr_img, caption="QR Entry Pass")
            st.code(pid)

    st.markdown("### 🚨 Alerts")
    for a in st.session_state.alerts[-5:]:
        st.warning(a)

# ======================================================
# 📊 DASHBOARD (FIXED + CLEAR DATA)
# ======================================================
elif page == "📊 Dashboard":

    st.markdown("<div class='title'>🚗 Park+ | Smart Campus Parking System</div>", unsafe_allow_html=True)
    st.caption("Mahindra University • AI-Powered Parking Control Dashboard")

    st.markdown("---")

    # ================= KPI =================
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Available Slots", sum(available.values()))
    c2.metric("Occupied Slots", total_used)
    c3.metric("Occupancy %", f"{occupancy}%")
    c4.metric("Total Capacity", TOTAL)

    st.markdown("---")

    # ================= CHART =================
    st.subheader("📊 Zone Occupancy")

    df_chart = pd.DataFrame({
        "Zone": list(occupied.keys()),
        "Used": list(occupied.values()),
        "Available": list(available.values())
    })

    st.bar_chart(df_chart.set_index("Zone"))

    # ================= TABLE =================
    st.subheader("🧾 Recent Reservations")

    if st.session_state.bookings:
        df = pd.DataFrame(st.session_state.bookings)
        st.dataframe(df, use_container_width=True, height=250)

        st.subheader("📈 Role Distribution")
        st.bar_chart(df["Role"].value_counts())

    else:
        st.info("No reservations yet")