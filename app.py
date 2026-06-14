import streamlit as st
import random
import hashlib
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

if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

# ================= ZONES =================
zones = {
    "Zone A (Faculty)": random.randint(65, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Visitors)": random.randint(20, 80)
}

TOTAL = 500
occupied = sum(zones.values())
available = TOTAL - occupied
occupancy = round((occupied / TOTAL) * 100, 2)

# ================= AI =================
def ai_zone(role):
    if role == "Faculty":
        return "Zone A (Faculty)"
    elif role == "Student":
        return "Zone B (Students)"
    return "Zone C (Visitors)"

def notify(msg):
    st.session_state.alerts.append(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")

def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# ================= STYLE (SAAS DASHBOARD LOOK) =================
st.markdown("""
<style>

.main {
    background-color: #0b1220;
    color: #e5e7eb;
}

/* HEADER */
.title {
    font-size: 28px;
    font-weight: 700;
    color: #60a5fa;
}

/* KPI CARD STYLE */
.card {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    text-align: center;
}

/* BUTTON */
.stButton button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<div class='title'>🚗 Park+ | Smart Campus Parking System</div>", unsafe_allow_html=True)
st.caption("Mahindra University • AI-Powered Parking Control Dashboard")

st.markdown("---")

# ================= KPI DASHBOARD (LIKE IMAGE) =================
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"<div class='card'><h4>Available Slots</h4><h2>{available}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><h4>Occupied Slots</h4><h2>{occupied}</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><h4>Occupancy %</h4><h2>{occupancy}%</h2></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><h4>Total Capacity</h4><h2>{TOTAL}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# ================= MAIN LAYOUT =================
left, right = st.columns([1.1, 2])

# ================= LEFT PANEL =================
with left:

    st.subheader("🎟 Smart Reservation Panel")

    role = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])
    vehicle = st.text_input("Vehicle Number")

    ai_suggestion = ai_zone(role)
    st.info(f"🤖 AI Suggestion → {ai_suggestion}")

    if st.button("Generate Parking Pass"):

        if vehicle:

            pid = "PARK+" + hashlib.md5((vehicle + str(datetime.now())).encode()).hexdigest()[:10].upper()

            qr_data = f"""
PARK+ CAMPUS
ID: {pid}
ROLE: {role}
ZONE: {ai_suggestion}
TIME: {datetime.now()}
"""

            qr_img = make_qr(qr_data)

            st.session_state.pass_id = pid

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Role": role,
                "Zone": ai_suggestion,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            notify(f"{role} booked {ai_suggestion}")

            st.success("Booking Confirmed")
            st.image(qr_img, caption="QR Entry Pass")
            st.code(pid)

        else:
            st.error("Enter vehicle number")

    st.markdown("### 🚨 Alerts")
    for a in st.session_state.alerts[-5:]:
        st.warning(a)

# ================= RIGHT DASHBOARD =================
with right:

    st.subheader("📊 Live Parking Dashboard")

    st.markdown("### Zone Occupancy")

    for z, v in zones.items():
        st.write(z)
        st.progress(v)

    st.markdown("### 📈 Occupancy Analytics")

    st.bar_chart(zones)

    st.markdown("### 🧾 Recent Reservations")

    if st.session_state.bookings:
        st.dataframe(st.session_state.bookings, use_container_width=True)
    else:
        st.info("No reservations yet")

# ================= FOOTER =================
st.markdown("---")
st.caption("Park+ Smart Campus System • Mahindra University")
import streamlit as st
import pandas as pd
import qrcode
import plotly.express as px
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Mahindra University Smart Parking",
    layout="wide"
)

st.title("🏫 Mahindra University Smart Parking System")

# ---------------- SESSION STATE ----------------
if "reservations" not in st.session_state:
    st.session_state.reservations = []

# ---------------- NAVIGATION ----------------
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation System", "📊 Analytics Dashboard"]
)

# ---------------- ZONES DATA ----------------
zones = [
    {"name": "Faculty Zone", "color": "green", "occupancy": 80},
    {"name": "Student Zone", "color": "blue", "occupancy": 60},
    {"name": "Visitor Zone", "color": "orange", "occupancy": 40},
]

# ======================================================
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":

    st.subheader("Campus Parking Zone Overview")

    st.markdown("""
    ### 🧭 Zone Legend
    🟢 Faculty Zone → Priority Parking  
    🔵 Student Zone → Regular Parking  
    🟠 Visitor Zone → Temporary Parking  
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"{zones[0]['name']}\n{zones[0]['occupancy']}% Occupied")

    with col2:
        st.info(f"{zones[1]['name']}\n{zones[1]['occupancy']}% Occupied")

    with col3:
        st.warning(f"{zones[2]['name']}\n{zones[2]['occupancy']}% Occupied")

    st.divider()

    st.subheader("📍 Campus Map (Simulation View)")

    map_data = pd.DataFrame({
        "lat": [17.543, 17.544, 17.542, 17.5435],
        "lon": [78.572, 78.573, 78.571, 78.5725]
    })

    st.map(map_data)

    st.info("Click zones (future upgrade: interactive polygon map with Leaflet)")

# ======================================================
# 🅿️ RESERVATION SYSTEM
# ======================================================
elif page == "🅿️ Reservation System":

    st.subheader("Reserve Your Parking Slot")

    st.markdown("Fill in details below to reserve a parking slot")

    vehicle = st.text_input("🚗 Vehicle Number (e.g., AP09AB1234)")

    zone = st.selectbox(
        "📍 Select Parking Zone",
        [z["name"] for z in zones]
    )

    time_slot = st.time_input("⏰ Select Time Slot")

    faculty_priority = st.checkbox("Faculty Priority Access")

    if st.button("🚀 Reserve Parking Slot"):

        if vehicle.strip() == "":
            st.error("Vehicle number is required")
        else:
            reservation = {
                "vehicle": vehicle,
                "zone": zone,
                "time": str(time_slot),
                "priority": "Faculty" if faculty_priority else "Normal"
            }

            st.session_state.reservations.append(reservation)

            # ---------------- QR GENERATION (SAFE) ----------------
            qr_data = str(reservation)
            qr_img = qrcode.make(qr_data)

            st.success("✅ Parking Reserved Successfully!")

            st.markdown("### 🎟️ Your Entry QR Code")
            st.image(qr_img, caption="Scan at Entry Gate")

            st.json(reservation)

    st.divider()

    st.subheader("📋 Recent Reservations")

    if st.session_state.reservations:
        st.dataframe(pd.DataFrame(st.session_state.reservations))
    else:
        st.info("No reservations yet")

# ======================================================
# 📊 ANALYTICS DASHBOARD
# ======================================================
elif page == "📊 Analytics Dashboard":

    st.subheader("Parking Usage Analytics")

    if len(st.session_state.reservations) == 0:
        st.warning("No data available yet")
    else:

        df = pd.DataFrame(st.session_state.reservations)

        st.dataframe(df)

        st.divider()

        # ---------------- ZONE ANALYSIS ----------------
        zone_count = df["zone"].value_counts().reset_index()
        zone_count.columns = ["Zone", "Count"]

        fig1 = px.bar(
            zone_count,
            x="Zone",
            y="Count",
            title="Zone-wise Reservations"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ---------------- PRIORITY ANALYSIS ----------------
        priority_count = df["priority"].value_counts().reset_index()
        priority_count.columns = ["Priority", "Count"]

        fig2 = px.pie(
            priority_count,
            names="Priority",
            values="Count",
            title="Faculty vs Normal Usage"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ---------------- METRICS ----------------
        st.metric("Total Reservations", len(df))
        st.metric("Most Used Zone", df["zone"].mode()[0])