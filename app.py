import streamlit as st
import random
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# ================= CONFIG =================
st.set_page_config(
    page_title="ParkSmart | Smart Campus Parking System",
    layout="wide",
    page_icon="🚗"
)

# ================= SESSION STATE =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "event_bookings" not in st.session_state:
    st.session_state.event_bookings = []

# ================= PREDEFINED EVENTS =================
EVENTS = [
    {"name": "Tech Fest 2026", "slots": 60, "booked": 0},
    {"name": "Convocation Day", "slots": 80, "booked": 0},
    {"name": "Hackathon Night", "slots": 40, "booked": 0}
]

# ================= BASE ZONES =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}

# ================= COMPUTE LIVE ZONES =================
def compute_zones():
    used = {z: 0 for z in BASE_ZONES}

    for b in st.session_state.bookings:
        if b["Zone"] in used:
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
.main { background-color: #0b1220; color: #e5e7eb; }

.title {
    font-size: 30px;
    font-weight: 800;
    color: #60a5fa;
}

.zoneA { background:#16a34a; padding:15px; border-radius:12px; color:white; text-align:center; }
.zoneB { background:#2563eb; padding:15px; border-radius:12px; color:white; text-align:center; }
.zoneC { background:#f59e0b; padding:15px; border-radius:12px; color:white; text-align:center; }

.stButton button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border-radius: 10px;
    width: 100%;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation System", "🎉 Event Parking", "📊 Dashboard"]
)

# ======================================================
# 🗺️ MAP VIEW (ZONE BASED)
# ======================================================
if page == "🗺️ Map View":

    st.markdown("<div class='title'>🗺️ ParkSmart Campus Map</div>", unsafe_allow_html=True)

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

    st.markdown("<div class='title'>🅿️ Parking Reservation</div>", unsafe_allow_html=True)

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

            qr_data = f"""
PARKSMART
ID: {pid}
ZONE: {zone}
TIME: {datetime.now()}
"""

            qr_img = make_qr(qr_data)

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Role": role,
                "Zone": zone,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            notify(f"{role} booked {zone}")

            st.success("Booking Confirmed 🚗")
            st.image(qr_img, caption="Entry QR")
            st.code(pid)

    st.markdown("### Alerts")
    for a in st.session_state.alerts[-5:]:
        st.warning(a)

# ======================================================
# 🎉 EVENT PARKING (NO CREATE EVENT — REAL TIME BOOKING)
# ======================================================
elif page == "🎉 Event Parking":

    st.markdown("<div class='title'>🎉 Event Parking (Live Booking)</div>", unsafe_allow_html=True)

    st.subheader("Upcoming Events")

    event_names = [e["name"] for e in EVENTS]

    selected_event = st.selectbox("Select Event", event_names)
    vehicle = st.text_input("Vehicle Number (Event Parking)")

    event_obj = next(e for e in EVENTS if e["name"] == selected_event)

    st.info(f"Slots Available: {event_obj['slots'] - event_obj['booked']} / {event_obj['slots']}")

    if st.button("Book Event Parking"):

        if vehicle.strip() == "":
            st.error("Enter vehicle number")

        elif event_obj["booked"] >= event_obj["slots"]:
            st.error("Event Parking Full")

        else:

            event_obj["booked"] += 1

            pid = "EVENT+" + hashlib.md5(
                (vehicle + selected_event + str(datetime.now())).encode()
            ).hexdigest()[:10].upper()

            qr_data = f"""
PARKSMART EVENT
EVENT: {selected_event}
VEHICLE: {vehicle}
TIME: {datetime.now()}
ID: {pid}
"""

            qr_img = make_qr(qr_data)

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Role": "Event User",
                "Zone": f"Event-{selected_event}",
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            st.session_state.event_bookings.append({
                "Event": selected_event,
                "Vehicle": vehicle,
                "Time": datetime.now().strftime("%H:%M:%S")
            })

            st.success("Event Parking Confirmed 🎉")
            st.image(qr_img, caption="Event QR Pass")
            st.code(pid)

    st.divider()

    st.subheader("📊 Event Status")
    st.dataframe(pd.DataFrame(EVENTS))

    st.subheader("🧾 Recent Event Bookings")

    if st.session_state.event_bookings:
        st.dataframe(pd.DataFrame(st.session_state.event_bookings))
    else:
        st.info("No event bookings yet")

# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":

    st.markdown("<div class='title'>📊 ParkSmart Dashboard</div>", unsafe_allow_html=True)

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Available Slots", sum(available.values()))
    c2.metric("Occupied Slots", total_used)
    c3.metric("Occupancy %", f"{occupancy}%")
    c4.metric("Total Capacity", TOTAL)

    st.markdown("---")

    st.subheader("Zone Analytics")
    st.bar_chart(occupied)

    st.subheader("Recent Bookings")

    if st.session_state.bookings:
        st.dataframe(pd.DataFrame(st.session_state.bookings))
    else:
        st.info("No bookings yet")

    st.markdown("---")

    st.subheader("🎉 Event Overview")
    st.dataframe(pd.DataFrame(EVENTS))