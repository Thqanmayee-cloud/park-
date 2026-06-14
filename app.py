import streamlit as st
import random
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# ================= CONFIG =================
st.set_page_config(
    page_title="ParkSmart | Mahindra University",
    layout="wide",
    page_icon="🚗"
)

# ================= BRAND HEADER =================
col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1e/Mahindra_University_logo.png", width=80)

with col_title:
    st.markdown("""
    # 🏫 Mahindra University
    ### ParkSmart – Smart Campus Parking System
    """)

st.markdown("---")

# ================= SESSION =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "event_bookings" not in st.session_state:
    st.session_state.event_bookings = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# ================= LOGIN (SIMPLE ADMIN) =================
if "admin" not in st.session_state:
    st.session_state.admin = False

if not st.session_state.admin:
    st.sidebar.subheader("🔐 Admin Login")
    pwd = st.sidebar.text_input("Enter Admin Password", type="password")

    if st.sidebar.button("Login"):
        if pwd == "admin123":
            st.session_state.admin = True
            st.success("Admin Login Success")
        else:
            st.error("Wrong Password")
    st.stop()

# ================= BASE DATA =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}

EVENTS = [
    {"name": "Tech Fest 2026", "slots": 60, "booked": 0},
    {"name": "Convocation Day", "slots": 80, "booked": 0},
    {"name": "Hackathon Night", "slots": 40, "booked": 0}
]

# ================= COMPUTE =================
def compute_zones():
    used = {z: 0 for z in BASE_ZONES}
    for b in st.session_state.bookings:
        if b["Zone"] in used:
            used[b["Zone"]] += 1

    available = {z: max(BASE_ZONES[z] - used[z], 0) for z in BASE_ZONES}
    return used, available

occupied, available = compute_zones()

TOTAL = sum(BASE_ZONES.values())
total_used = sum(occupied.values())
occupancy = round((total_used / TOTAL) * 100, 2)

# ================= HELPERS =================
def ai_zone(role):
    return {
        "Faculty": "Zone A (Faculty)",
        "Student": "Zone B (Students)"
    }.get(role, "Zone C (Visitors)")

def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation", "🎉 Event Parking", "📷 QR Scanner", "📊 Dashboard"]
)

# ======================================================
# 🗺️ MAP VIEW (CAMPUS STYLE)
# ======================================================
if page == "🗺️ Map View":

    st.title("🗺️ Campus Parking Map")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("🟢 Zone A - Faculty")
        st.metric("Available", available["Zone A (Faculty)"])
        st.metric("Occupied", occupied["Zone A (Faculty)"])
        st.progress(occupied["Zone A (Faculty)"] / BASE_ZONES["Zone A (Faculty)"])

    with col2:
        st.info("🔵 Zone B - Students")
        st.metric("Available", available["Zone B (Students)"])
        st.metric("Occupied", occupied["Zone B (Students)"])
        st.progress(occupied["Zone B (Students)"] / BASE_ZONES["Zone B (Students)"])

    with col3:
        st.warning("🟡 Zone C - Visitors")
        st.metric("Available", available["Zone C (Visitors)"])
        st.metric("Occupied", occupied["Zone C (Visitors)"])
        st.progress(occupied["Zone C (Visitors)"] / BASE_ZONES["Zone C (Visitors)"])

# ======================================================
# 🅿️ RESERVATION SYSTEM
# ======================================================
elif page == "🅿️ Reservation":

    st.title("🅿️ Parking Reservation")

    role = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])
    vehicle = st.text_input("Vehicle Number")

    zone = ai_zone(role)
    st.info(f"AI Suggested Zone → {zone}")

    if st.button("Book Parking"):

        pid = "PSMART+" + hashlib.md5(
            (vehicle + str(datetime.now())).encode()
        ).hexdigest()[:10].upper()

        st.session_state.bookings.append({
            "Vehicle": vehicle,
            "Role": role,
            "Zone": zone,
            "Time": datetime.now().strftime("%H:%M:%S")
        })

        qr = make_qr(pid)

        st.success("Booked Successfully 🚗")
        st.image(qr, caption="Entry QR")
        st.code(pid)

# ======================================================
# 🎉 EVENT PARKING (LIVE BOOKING)
# ======================================================
elif page == "🎉 Event Parking":

    st.title("🎉 Event Parking")

    event = st.selectbox("Select Event", [e["name"] for e in EVENTS])
    vehicle = st.text_input("Vehicle Number (Event)")

    event_obj = next(e for e in EVENTS if e["name"] == event)

    st.info(f"Slots: {event_obj['slots'] - event_obj['booked']} / {event_obj['slots']}")

    if st.button("Book Event Slot"):

        if event_obj["booked"] < event_obj["slots"]:

            event_obj["booked"] += 1

            pid = "EVENT+" + hashlib.md5(
                (vehicle + event + str(datetime.now())).encode()
            ).hexdigest()[:10].upper()

            st.session_state.event_bookings.append({
                "Event": event,
                "Vehicle": vehicle,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            qr = make_qr(pid)

            st.success("Event Booked 🎉")
            st.image(qr)

        else:
            st.error("Event Full")

# ======================================================
# 📷 QR SCANNER (SIMULATED)
# ======================================================
elif page == "📷 QR Scanner":

    st.title("📷 Entry QR Scanner (Simulation)")

    code = st.text_input("Scan / Enter QR Code ID")

    if st.button("Validate"):

        if code.startswith("PSMART") or code.startswith("EVENT"):
            st.success("✅ Access Granted")
        else:
            st.error("❌ Invalid QR")

# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":

    st.title("📊 Analytics Dashboard")

    st.metric("Occupancy %", f"{occupancy}%")
    st.metric("Total Vehicles", total_used)

    st.bar_chart(pd.DataFrame(occupied, index=["Count"]).T)

    st.subheader("Recent Bookings")
    if st.session_state.bookings:
        st.dataframe(pd.DataFrame(st.session_state.bookings))

    st.subheader("Event Bookings")
    if st.session_state.event_bookings:
        st.dataframe(pd.DataFrame(st.session_state.event_bookings))