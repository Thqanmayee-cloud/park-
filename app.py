import streamlit as st
import random
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image

# ================= CONFIG =================
st.set_page_config(
    page_title="Park+ | Mahindra University",
    layout="wide",
    page_icon="🚗"
)

# ================= LOAD LOGO =================
logo_path = "/mnt/data/32816.jpg"

# ================= SESSION STATE =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

# ================= ZONES (3 ZONES AS PER SYSTEM) =================
zones = {
    "Zone A (Faculty)": random.randint(60, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Visitors)": random.randint(20, 80)
}

total_capacity = 500
occupied = sum(zones.values())
available = total_capacity - occupied
occupancy = round((occupied / total_capacity) * 100, 2)

# ================= AI ENGINE =================
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

# ================= CUSTOM CSS =================
st.markdown("""
<style>

.main {
    background-color: #0b1220;
    color: #e5e7eb;
}

.card {
    background: #0f172a;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    margin-bottom: 10px;
}

.big-title {
    font-size: 32px;
    font-weight: 700;
    color: #60a5fa;
}

.stButton button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER (LIKE IMAGE DASHBOARD) =================
col1, col2 = st.columns([1, 6])

with col1:
    st.image(logo_path, width=80)

with col2:
    st.markdown("<div class='big-title'>Park+ | Smart Campus Parking System</div>", unsafe_allow_html=True)
    st.caption("Mahindra University • AI-Powered Parking Control Center")

st.markdown("---")

# ================= TOP METRIC CARDS =================
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"<div class='card'><h4>Available Slots</h4><h2>{available}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><h4>Occupied Slots</h4><h2>{occupied}</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><h4>Occupancy</h4><h2>{occupancy}%</h2></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><h4>Total Capacity</h4><h2>{total_capacity}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# ================= MAIN DASHBOARD LAYOUT =================
left, right = st.columns([1.2, 2])

# ================= LEFT PANEL (BOOKING + AI) =================
with left:

    st.subheader("🎟 Smart Reservation")

    role = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])
    vehicle = st.text_input("Vehicle Number")

    recommended = ai_zone(role)
    st.info(f"🤖 AI Suggestion → {recommended}")

    if st.button("Generate Parking Pass"):

        if vehicle:

            pid = "PARK+" + hashlib.md5((vehicle+str(datetime.now())).encode()).hexdigest()[:10].upper()

            qr_data = f"""
PARK+ MAHINDRA UNIVERSITY
ID: {pid}
ROLE: {role}
ZONE: {recommended}
TIME: {datetime.now()}
"""

            qr_img = make_qr(qr_data)

            st.session_state.pass_id = pid

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Role": role,
                "Zone": recommended,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            notify(f"{role} booked {recommended}")

            st.success("Booking Confirmed")
            st.image(qr_img, caption="QR Entry Pass")
            st.code(pid)

        else:
            st.error("Enter vehicle number")

    st.markdown("### 🚨 Live Alerts")

    for a in st.session_state.alerts[-5:]:
        st.warning(a)

# ================= RIGHT PANEL (DASHBOARD LIKE IMAGE) =================
with right:

    st.subheader("📊 Parking Analytics Dashboard")

    st.markdown("### Zone Occupancy Overview")

    for z, v in zones.items():
        st.write(z)
        st.progress(v)

    st.markdown("### 📈 Occupancy Chart")

    st.bar_chart(zones)

    st.markdown("### 🧾 Recent Reservations")

    if st.session_state.bookings:
        st.dataframe(st.session_state.bookings, use_container_width=True)
    else:
        st.info("No reservations yet")

# ================= FOOTER =================
st.markdown("---")
st.caption("Park+ Smart Campus System • Mahindra University • AI Control Dashboard")