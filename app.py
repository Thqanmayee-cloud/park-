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

if "events" not in st.session_state:
    st.session_state.events = []

# ================= BASE ZONES =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}

# ================= COMPUTE ZONES =================
def compute_zones():
    used = {z: 0 for z in BASE_ZONES}

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
    st.session_state.alerts.append(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")

# ================= STYLE =================
st.markdown("""
<style>
.main { background-color: #0b1220; color: #e5e7eb; }

.title {
    font-size: 30px;
    font-weight: 800;
    color: #60a5fa;
}

.zoneA { background:#16a34a; padding:15px; border-radius:10px; color:white; text-align:center; }
.zoneB { background:#2563eb; padding:15px; border-radius:10px; color:white; text-align:center; }
.zoneC { background:#f59e0b; padding:15px; border-radius:10px; color:white; text-align:center; }

.card {
    background:#111827;
    padding:15px;
    border-radius:10px;
    text-align:center;
    border:1px solid #1f2937;
}

.stButton button {
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    width:100%;
    border-radius:10px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation System", "🎉 Event Parking", "📊 Dashboard"]
)

# ======================================================
# 🗺️ MAP VIEW (ZONE MAP)
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
# 🎉 EVENT PARKING SYSTEM
# ======================================================
elif page == "🎉 Event Parking":

    st.markdown("<div class='title'>🎉 Event Parking System</div>", unsafe_allow_html=True)

    # -------- CREATE EVENT --------
    st.subheader("Create Event")

    name = st.text_input("Event Name")
    date = st.date_input("Event Date")
    slots = st.number_input("Parking Slots", 10, 1000, 50)

    if st.button("Create Event"):

        if name.strip() == "":
            st.error("Enter event name")
        else:
            st.session_state.events.append({
                "name": name,
                "date": str(date),
                "slots": slots,
                "booked": 0
            })
            st.success("Event Created")

    st.divider()

    # -------- SHOW EVENTS --------
    st.subheader("Upcoming Events")

    if st.session_state.events:
        st.dataframe(pd.DataFrame(st.session_state.events))
    else:
        st.info("No events yet")

    st.divider()

    # -------- BOOK EVENT PARKING --------
    st.subheader("Book Event Parking")

    if st.session_state.events:

        event = st.selectbox("Select Event", [e["name"] for e in st.session_state.events])
        vehicle = st.text_input("Vehicle Number (Event)")

        if st.button("Reserve Event Parking"):

            for e in st.session_state.events:

                if e["name"] == event:

                    if e["booked"] >= e["slots"]:
                        st.error("Event Full")
                    else:

                        e["booked"] += 1

                        pid = "EVENT+" + hashlib.md5(
                            (vehicle + str(datetime.now())).encode()
                        ).hexdigest()[:10].upper()

                        st.session_state.bookings.append({
                            "Vehicle": vehicle,
                            "Role": "Event User",
                            "Zone": f"Event-{event}",
                            "Time": datetime.now().strftime("%H:%M:%S")
                        })

                        st.success("Event Parking Confirmed 🎉")
                        st.code(pid)

    else:
        st.warning("Create an event first")

# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":

    st.markdown("<div class='title'>📊 ParkSmart Dashboard</div>", unsafe_allow_html=True)

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Available", sum(available.values()))
    c2.metric("Occupied", total_used)
    c3.metric("Occupancy %", f"{occupancy}%")
    c4.metric("Total", TOTAL)

    st.markdown("---")

    st.subheader("Zone Analytics")
    st.bar_chart(occupied)

    st.subheader("Reservations")

    if st.session_state.bookings:
        st.dataframe(pd.DataFrame(st.session_state.bookings))
    else:
        st.info("No bookings yet")

    st.markdown("---")

    st.subheader("🎉 Event Overview")

    if st.session_state.events:
        st.dataframe(pd.DataFrame(st.session_state.events))
    else:
        st.info("No events created yet")