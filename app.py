import streamlit as st
import random
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO

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
available = max(TOTAL - occupied, 0)   # FIX: prevent negative values
occupancy = round((occupied / TOTAL) * 100, 2)

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

.main {
    background-color: #0b1220;
    color: #e5e7eb;
}

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

# ================= HEADER =================
st.markdown("<div class='title'>🚗 Park+ | Smart Campus Parking System</div>", unsafe_allow_html=True)
st.caption("Mahindra University • AI-Powered Parking Control Dashboard")

st.markdown("---")

# ================= KPI DASHBOARD =================
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

        if vehicle.strip() == "":
            st.error("Enter vehicle number")

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