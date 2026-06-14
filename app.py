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

# ================= TITLE =================
st.title("🏫 ParkSmart | Mahindra University Smart Parking System")
st.markdown("---")

# ================= SESSION =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "event_bookings" not in st.session_state:
    st.session_state.event_bookings = []

# ================= BASE ZONES =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}

# ================= PREDEFINED EVENTS =================
EVENTS = [
    {"name": "Tech Fest 2026", "slots": 60, "booked": 0},
    {"name": "Convocation Day", "slots": 80, "booked": 0},
    {"name": "Hackathon Night", "slots": 40, "booked": 0}
]

# ================= COMPUTE ZONES =================
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
    if role == "Faculty":
        return "Zone A (Faculty)"
    elif role == "Student":
        return "Zone B (Students)"
    return "Zone C (Visitors)"

def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

def notify(msg):
    st.session_state.alerts.append(
        f"{datetime.now().strftime('%H:%M:%S')} - {msg}"
    )

# ================= STYLE =================
st.markdown("""
<style>
.zoneA {background:#16a34a;padding:12px;border-radius:10px;color:white;text-align:center;}
.zoneB {background:#2563eb;padding:12px;border-radius:10px;color:white;text-align:center;}
.zoneC {background:#f59e0b;padding:12px;border-radius:10px;color:white;text-align:center;}

.stButton button {
    width:100%;
    border-radius:10px;
    font-weight:bold;
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation System", "🎉 Event Parking", "📊 Dashboard"]
)

# ======================================================
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":

    st.title("🗺️ Campus Parking Map")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='zoneA'>ZONE A<br>FACULTY</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone A (Faculty)"])
        st.metric("Occupied", occupied["Zone A (Faculty)"])

    with col2:
        st.markdown("<div class='zoneB'>ZONE B<br>STUDENTS</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone B (Students)"])
        st.metric("Occupied", occupied["Zone B (Students)"])

    with col3:
        st.markdown("<div class='zoneC'>ZONE C<br>VISITORS</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone C (Visitors)"])
        st.metric("Occupied", occupied["Zone C (Visitors)"])

# ======================================================
# 🅿️ RESERVATION SYSTEM
# ======================================================
elif page == "🅿️ Reservation System":

    st.title("🅿️ Parking Reservation")

    role = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])
    vehicle = st.text_input("Vehicle Number")

    zone = ai_zone(role)
    st.info(f"AI Suggested Zone → {zone}")

    if st.button("Generate Parking Pass"):

        if vehicle.strip() == "":
            st.error("Enter vehicle number")

        elif available[zone] <= 0:
            st.error("No slots available")

        else:

            pid = "PSMART+" + hashlib.md5(
                (vehicle + str(datetime.now())).encode()
            ).hexdigest()[:10].upper()

            qr = make_qr(pid)

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Role": role,
                "Zone": zone,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            notify(f"{role} booked {zone}")

            st.success("Booking Confirmed 🚗")
            st.image(qr)
            st.code(pid)

    for a in st.session_state.alerts[-5:]:
        st.warning(a)

# ======================================================
# 🎉 EVENT PARKING
# ======================================================
elif page == "🎉 Event Parking":

    st.title("🎉 Event Parking System")

    event_name = st.selectbox("Select Event", [e["name"] for e in EVENTS])
    vehicle = st.text_input("Vehicle Number (Event)")

    event_obj = next(e for e in EVENTS if e["name"] == event_name)

    st.info(f"Slots Available: {event_obj['slots'] - event_obj['booked']} / {event_obj['slots']}")

    if st.button("Book Event Parking"):

        if vehicle.strip() == "":
            st.error("Enter vehicle number")

        elif event_obj["booked"] >= event_obj["slots"]:
            st.error("Event Parking Full")

        else:

            event_obj["booked"] += 1

            pid = "EVENT+" + hashlib.md5(
                (vehicle + event_name + str(datetime.now())).encode()
            ).hexdigest()[:10].upper()

            qr = make_qr(pid)

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Role": "Event User",
                "Zone": f"Event-{event_name}",
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            st.session_state.event_bookings.append({
                "Event": event_name,
                "Vehicle": vehicle,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            st.success("Event Parking Confirmed 🎉")
            st.image(qr)
            st.code(pid)

    st.divider()
    st.subheader("📊 Event Overview")
    st.dataframe(pd.DataFrame(EVENTS))

# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":

    st.title("📊 ParkSmart Dashboard")

    st.metric("Occupancy %", f"{occupancy}%")
    st.metric("Total Vehicles", total_used)

    st.subheader("Zone Status")
    st.bar_chart(pd.DataFrame(occupied, index=["Count"]).T)

    st.subheader("Recent Bookings")

    if st.session_state.bookings:
        st.dataframe(pd.DataFrame(st.session_state.bookings))

    st.subheader("Event Bookings")

    if st.session_state.event_bookings:
        st.dataframe(pd.DataFrame(st.session_state.event_bookings))