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


# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf


# ======================================================
# 🚨 LOGIN PAGE (CENTER FIX - NO BACKGROUND CHANGE)
# ======================================================
if not st.session_state.logged_in:

    st.markdown("""
    <style>

    .login-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;

        display: flex;
        justify-content: center;
        align-items: center;
    }

    .login-box {
        width: 420px;
        padding: 40px;
        background: #111827;
        border-radius: 18px;
        box-shadow: 0px 12px 40px rgba(0,0,0,0.45);
        text-align: center;
    }

    .title {
        font-size: 32px;
        font-weight: bold;
        color: #60a5fa;
    }

    .subtitle {
        color: #9ca3af;
        margin-bottom: 25px;
        font-size: 14px;
    }

    .hint {
        font-size: 12px;
        color: #9ca3af;
        margin-top: 10px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg,#2563eb,#1d4ed8);
        color: white;
        font-weight: bold;
        padding: 10px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>🏫 ParkSmart</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Mahindra University Smart Parking System</div>", unsafe_allow_html=True)

    email = st.text_input("University Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        role = get_role(email)

        if role is None:
            st.error("Invalid university email")

        else:
            if role == "Student" and password == "student123":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = email
                st.rerun()

            elif role == "Faculty" and password == "faculty123":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = email
                st.rerun()

            else:
                st.error("Wrong password")

    st.markdown("""
    <div class='hint'>
    Demo Credentials:<br>
    👨‍🎓 Student → student123<br>
    👨‍🏫 Faculty → faculty123
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ================= SIDEBAR =================
st.sidebar.success(f"Logged in as {st.session_state.role}")
st.sidebar.write(st.session_state.user)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()


# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Parking", "🎉 Events", "📊 Dashboard"]
)


# ======================================================
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":

    st.title("🗺️ Campus Parking Zones")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Zone A (Faculty)", random.randint(60, 100))

    with col2:
        st.metric("Zone B (Students)", random.randint(80, 150))

    with col3:
        st.metric("Zone C (Visitors)", random.randint(30, 70))


# ======================================================
# 🅿️ PARKING
# ======================================================
elif page == "🅿️ Parking":

    st.title("🅿️ Parking Reservation")

    vehicle = st.text_input("Vehicle Number")

    zone = "Zone A (Faculty)" if st.session_state.role == "Faculty" else "Zone B (Student)"

    st.info(f"Assigned Zone: {zone}")

    if st.button("Book Parking"):

        pid = hashlib.md5((vehicle + str(datetime.now())).encode()).hexdigest()[:10]

        st.session_state.bookings.append({
            "User": st.session_state.user,
            "Vehicle": vehicle,
            "Zone": zone,
            "Time": str(datetime.now())
        })

        st.success("Booking Confirmed")
        st.image(make_qr(pid))
        st.code(pid)


# ======================================================
# 🎉 EVENTS
# ======================================================
elif page == "🎉 Events":

    st.title("🎉 Event Parking")

    event = st.selectbox("Select Event", ["Tech Fest", "Convocation"])
    vehicle = st.text_input("Vehicle Number")

    if st.button("Book Event Slot"):

        pid = hashlib.md5((vehicle + event + str(datetime.now())).encode()).hexdigest()[:10]

        st.session_state.event_bookings.append({
            "User": st.session_state.user,
            "Event": event,
            "Vehicle": vehicle,
            "Time": str(datetime.now())
        })

        st.success("Event Booking Confirmed")
        st.image(make_qr(pid))
        st.code(pid)


# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":

    st.title("📊 Parking Analytics")

    st.metric("Total Parking Bookings", len(st.session_state.bookings))
    st.metric("Event Bookings", len(st.session_state.event_bookings))

    st.subheader("Parking Data")
    st.dataframe(pd.DataFrame(st.session_state.bookings))

    st.subheader("Event Data")
    st.dataframe(pd.DataFrame(st.session_state.event_bookings))