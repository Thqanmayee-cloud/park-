import streamlit as st
import random
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ParkSmart", layout="wide", page_icon="🚗")

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
    st.session_state.user = None

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "event_bookings" not in st.session_state:
    st.session_state.event_bookings = []


# ================= ROLE DETECTION =================
def get_role(email):
    if "@mahindrauniversity.edu.in" not in email:
        return None
    prefix = email.split("@")[0]
    return "Student" if prefix[:2].isdigit() else "Faculty"


# ================= LOGIN GATE =================
if not st.session_state.logged_in:

    st.title("🏫 ParkSmart Login")
    st.markdown("---")

    email = st.text_input("University Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        role = get_role(email)

        if role is None:
            st.error("Invalid university email")

        elif password.strip() == "":
            st.error("Enter password")

        else:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.user = email
            st.rerun()

    st.stop()


# ================= LOGGED IN HEADER =================
st.sidebar.success(f"Logged in as {st.session_state.role}")
st.sidebar.write(st.session_state.user)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()


# ================= BASE DATA =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}

EVENTS = [
    {"name": "Tech Fest", "slots": 60, "booked": 0},
    {"name": "Convocation", "slots": 80, "booked": 0}
]


# ================= ZONE CALC =================
def compute_zones():
    used = {z: 0 for z in BASE_ZONES}

    for b in st.session_state.bookings:
        if b["Zone"] in used:
            used[b["Zone"]] += 1

    available = {z: BASE_ZONES[z] - used[z] for z in BASE_ZONES}
    return used, available


occupied, available = compute_zones()


# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf


# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation", "🎉 Events", "📊 Dashboard"]
)


# ======================================================
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":

    st.title("🗺️ Parking Zones")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Zone A (Faculty)", available["Zone A (Faculty)"])
        st.metric("Occupied", occupied["Zone A (Faculty)"])

    with col2:
        st.metric("Zone B (Students)", available["Zone B (Students)"])
        st.metric("Occupied", occupied["Zone B (Students)"])

    with col3:
        st.metric("Zone C (Visitors)", available["Zone C (Visitors)"])
        st.metric("Occupied", occupied["Zone C (Visitors)"])


# ======================================================
# 🅿️ RESERVATION
# ======================================================
elif page == "🅿️ Reservation":

    st.title("🅿️ Parking Reservation")

    role = st.session_state.role
    vehicle = st.text_input("Vehicle Number")

    zone = "Zone A (Faculty)" if role == "Faculty" else "Zone B (Students)"

    st.info(f"Assigned Zone → {zone}")

    if st.button("Book Parking"):

        pid = "PSMART+" + hashlib.md5(
            (vehicle + str(datetime.now())).encode()
        ).hexdigest()[:10].upper()

        st.session_state.bookings.append({
            "User": st.session_state.user,
            "Vehicle": vehicle,
            "Zone": zone,
            "Time": str(datetime.now())
        })

        qr = make_qr(pid)

        st.success("Booking Confirmed")
        st.image(qr)
        st.code(pid)


# ======================================================
# 🎉 EVENTS
# ======================================================
elif page == "🎉 Events":

    st.title("🎉 Event Parking")

    event = st.selectbox("Event", ["Tech Fest", "Convocation"])
    vehicle = st.text_input("Vehicle")

    if st.button("Book Event"):

        pid = "EVENT+" + hashlib.md5(
            (vehicle + event + str(datetime.now())).encode()
        ).hexdigest()[:10].upper()

        st.session_state.event_bookings.append({
            "User": st.session_state.user,
            "Event": event,
            "Vehicle": vehicle,
            "Time": str(datetime.now())
        })

        qr = make_qr(pid)

        st.success("Event Booked")
        st.image(qr)
        st.code(pid)


# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":

    st.title("📊 Dashboard")

    st.metric("Total Parking Bookings", len(st.session_state.bookings))
    st.metric("Event Bookings", len(st.session_state.event_bookings))

    st.subheader("Parking Data")
    st.dataframe(pd.DataFrame(st.session_state.bookings))

    st.subheader("Event Data")
    st.dataframe(pd.DataFrame(st.session_state.event_bookings))