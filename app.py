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

# ================= ZONES (STABLE LOGIC) =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}

def calculate_zones():
    usage = {"Zone A (Faculty)": 0, "Zone B (Students)": 0, "Zone C (Visitors)": 0}

    for b in st.session_state.bookings:
        usage[b["Zone"]] += 1

    available = {
        z: max(BASE_ZONES[z] - usage[z], 0)
        for z in BASE_ZONES
    }

    return available, usage

available, occupied = calculate_zones()

TOTAL = sum(BASE_ZONES.values())
total_used = sum(occupied.values())
occupancy = round((total_used / TOTAL) * 100, 2)

# ================= AI =================
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
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":

    st.subheader("Campus Parking Zones")

    st.info("""
    🟢 Faculty Zone → Priority Parking  
    🔵 Student Zone → Standard Parking  
    🟡 Visitor Zone → Temporary Parking
    """)

    col1, col2, col3 = st.columns(3)

    col1.success(f"Faculty Zone\n{available['Zone A (Faculty)']} Slots")
    col2.info(f"Student Zone\n{available['Zone B (Students)']} Slots")
    col3.warning(f"Visitor Zone\n{available['Zone C (Visitors)']} Slots")

    st.map({
        "lat": [17.543, 17.544, 17.542],
        "lon": [78.572, 78.573, 78.571]
    })

# ======================================================
# 🅿️ RESERVATION SYSTEM
# ======================================================
elif page == "🅿️ Reservation System":

    st.subheader("🎟 Smart Reservation Panel")

    role = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])
    vehicle = st.text_input("Vehicle Number")

    ai_suggestion = ai_zone(role)
    st.info(f"🤖 AI Suggestion → {ai_suggestion}")

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

            st.success("Booking Confirmed")
            st.image(qr_img, caption="QR Entry Pass")
            st.code(pid)

    st.markdown("### 🚨 Alerts")
    for a in st.session_state.alerts[-5:]:
        st.warning(a)

# ======================================================
# 📊 DASHBOARD (ONLY TITLE HERE)
# ======================================================
elif page == "📊 Dashboard":

    st.markdown("<div class='title'>🚗 Park+ | Smart Campus Parking System</div>", unsafe_allow_html=True)
    st.caption("Mahindra University • AI-Powered Parking Control Dashboard")

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"<div class='card'><h4>Available</h4><h2>{sum(available.values())}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><h4>Occupied</h4><h2>{total_used}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><h4>Occupancy %</h4><h2>{occupancy}%</h2></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card'><h4>Total Capacity</h4><h2>{TOTAL}</h2></div>", unsafe_allow_html=True)

    st.markdown("---")

    st.bar_chart(occupied)

    st.markdown("### 🧾 Recent Reservations")

    if st.session_state.bookings:
        st.dataframe(st.session_state.bookings, use_container_width=True)
    else:
        st.info("No reservations yet")