import streamlit as st
import random
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ParkSmart", layout="wide", page_icon="🚗")


# ================= SESSION STATE =================
if "role" not in st.session_state:
    st.session_state.role = None

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "vehicle": ""
    }

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "event_bookings" not in st.session_state:
    st.session_state.event_bookings = []


# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf


# ======================================================
# ROLE SELECTION (NO LOGIN, SIMPLE & CLEAN)
# ======================================================
if st.session_state.role is None:

    st.title("ParkSmart - Smart Parking System")

    st.subheader("Select Your Role")

    role = st.radio("I am a:", ["Student", "Faculty"])

    name = st.text_input("Enter Your Name")

    vehicle = st.text_input("Default Vehicle Number (optional)")

    if st.button("Continue"):

        if name.strip() == "":
            st.error("Please enter your name")
        else:
            st.session_state.role = role
            st.session_state.profile["name"] = name
            st.session_state.profile["vehicle"] = vehicle
            st.rerun()

    st.stop()


# ================= SIDEBAR =================
st.sidebar.success(f"Role: {st.session_state.role}")
st.sidebar.write("User:", st.session_state.profile["name"])

if st.sidebar.button("Reset Session"):
    st.session_state.role = None
    st.rerun()


# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["Map View", "Parking", "Events", "Dashboard", "Profile"]
)


# ======================================================
# MAP VIEW
# ======================================================
if page == "Map View":

    st.title("Campus Parking Zones")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Zone A (Faculty)", random.randint(60, 100))

    with col2:
        st.metric("Zone B (Students)", random.randint(80, 150))

    with col3:
        st.metric("Zone C (Visitors)", random.randint(30, 70))


# ======================================================
# PARKING
# ======================================================
elif page == "Parking":

    st.title("Parking Reservation")

    vehicle = st.text_input("Vehicle Number", value=st.session_state.profile["vehicle"])

    zone = "Zone A (Faculty)" if st.session_state.role == "Faculty" else "Zone B (Student)"

    st.info(f"Assigned Zone: {zone}")

    if st.button("Book Parking"):

        pid = hashlib.md5((vehicle + str(datetime.now())).encode()).hexdigest()[:10]

        st.session_state.bookings.append({
            "User": st.session_state.profile["name"],
            "Role": st.session_state.role,
            "Vehicle": vehicle,
            "Zone": zone,
            "Time": str(datetime.now())
        })

        st.success("Booking Confirmed")
        st.image(make_qr(pid))
        st.code(pid)


# ======================================================
# EVENTS
# ======================================================
elif page == "Events":

    st.title("Event Parking")

    event = st.selectbox("Select Event", ["Tech Fest", "Convocation"])
    vehicle = st.text_input("Vehicle Number", value=st.session_state.profile["vehicle"])

    if st.button("Book Event Slot"):

        pid = hashlib.md5((vehicle + event + str(datetime.now())).encode()).hexdigest()[:10]

        st.session_state.event_bookings.append({
            "User": st.session_state.profile["name"],
            "Role": st.session_state.role,
            "Event": event,
            "Vehicle": vehicle,
            "Time": str(datetime.now())
        })

        st.success("Event Booking Confirmed")
        st.image(make_qr(pid))
        st.code(pid)


# ======================================================
# DASHBOARD
# ======================================================
elif page == "Dashboard":

    st.title("Parking Analytics")

    st.metric("Total Parking Bookings", len(st.session_state.bookings))
    st.metric("Event Bookings", len(st.session_state.event_bookings))

    st.subheader("Parking Data")
    st.dataframe(pd.DataFrame(st.session_state.bookings))

    st.subheader("Event Data")
    st.dataframe(pd.DataFrame(st.session_state.event_bookings))


# ======================================================
# PROFILE PAGE (EDITABLE)
# ======================================================
elif page == "Profile":

    st.title("Profile")

    st.session_state.profile["name"] = st.text_input(
        "Name",
        value=st.session_state.profile["name"]
    )

    st.session_state.profile["vehicle"] = st.text_input(
        "Vehicle Number",
        value=st.session_state.profile["vehicle"]
    )

    st.success("Profile is editable and saved automatically")