import streamlit as st
import random
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO

# ================= CONFIG =================
st.set_page_config(
    page_title="PARK+ Control Tower",
    layout="wide",
    page_icon="🚗"
)

# ================= STATE =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

# ================= ZONES =================
zones = {
    "Zone A (Faculty)": random.randint(60, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Visitors)": random.randint(20, 80)
}

total_capacity = 500
occupied = sum(zones.values())
available = total_capacity - occupied
occupancy = round((occupied / total_capacity) * 100, 2)

# ================= HELPERS =================
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

# ================= UI =================
st.title("🚗 PARK+ Smart Campus Control Tower")

# ================= LEFT CONTROL PANEL =================
col1, col2 = st.columns([1, 2])

with col1:

    st.subheader("🎟 Booking Panel")

    role = st.selectbox("Role", ["Student", "Faculty", "Visitor"])
    vehicle = st.text_input("Vehicle Number")

    recommended = ai_zone(role)
    st.info(f"AI Suggests → {recommended}")

    if st.button("Generate Parking Pass"):

        if vehicle:

            pid = "PARK+" + hashlib.md5((vehicle+str(datetime.now())).encode()).hexdigest()[:10].upper()

            qr_data = f"""
PARK+ PASS
ID: {pid}
ROLE: {role}
ZONE: {recommended}
TIME: {datetime.now()}
"""

            qr_img = make_qr(qr_data)

            st.session_state.pass_id = pid

            st.session_state.bookings.append({
                "id": pid,
                "vehicle": vehicle,
                "role": role,
                "zone": recommended,
                "time": datetime.now().strftime("%H:%M:%S")
            })

            notify(f"{role} booked {recommended}")

            st.success("Booking Successful")
            st.image(qr_img, caption="QR Pass")
            st.code(pid)

        else:
            st.error("Enter vehicle number")

    st.subheader("🚨 Traffic Alerts")
    for a in st.session_state.alerts[-5:]:
        st.warning(a)

# ================= RIGHT LIVE DASHBOARD =================
with col2:

    st.subheader("📊 Live Parking Control Center")

    c1, c2, c3 = st.columns(3)
    c1.metric("Available Slots", available)
    c2.metric("Occupied Slots", occupied)
    c3.metric("Occupancy %", f"{occupancy}%")

    st.markdown("### 🅿️ Zone Heatmap")

    for z, v in zones.items():
        st.write(z)
        st.progress(v)

    st.markdown("### 🧾 Reservations Table")

    if st.session_state.bookings:
        st.dataframe(st.session_state.bookings)
    else:
        st.info("No bookings yet")

    st.markdown("### 📈 Occupancy Chart")

    chart_data = {
        "Zone": list(zones.keys()),
        "Occupancy": list(zones.values())
    }

    st.bar_chart(chart_data, x="Zone", y="Occupancy")

# ================= PASS STATUS =================
st.markdown("---")
st.subheader("🎫 Active Pass")

if st.session_state.pass_id:
    st.success(st.session_state.pass_id)
else:
    st.info("No active pass")