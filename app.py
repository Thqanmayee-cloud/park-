import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# ================= CONFIG =================
st.set_page_config(page_title="ParkSmart System", layout="wide")

# ================= SESSION INIT =================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

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

# ================= AUTH FUNCTIONS =================
def register(email, name, password):
    role = get_role(email)
    if role is None:
        return "Invalid university email"

    if email in st.session_state.users:
        return "User already exists"

    st.session_state.users[email] = {
        "name": name,
        "password": password,
        "role": role
    }
    return "Registered Successfully"


def login(email, password):
    if email not in st.session_state.users:
        return "User not found"

    if st.session_state.users[email]["password"] != password:
        return "Wrong password"

    st.session_state.logged_in = True
    st.session_state.current_user = email
    return "Login Successful"


def change_password(email, old, new):
    if st.session_state.users[email]["password"] != old:
        return "Old password incorrect"

    st.session_state.users[email]["password"] = new
    return "Password updated"


def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None


# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf


# ================= AUTH PAGE =================
if not st.session_state.logged_in:

    st.title("🏫 ParkSmart Login System")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---------------- LOGIN ----------------
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            msg = login(email, password)
            if msg == "Login Successful":
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # ---------------- REGISTER ----------------
    with tab2:
        email = st.text_input("Email", key="reg_email")
        name = st.text_input("Full Name")
        password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register"):
            msg = register(email, name, password)
            if msg == "Registered Successfully":
                st.success(msg)
            else:
                st.error(msg)

    st.stop()


# ================= USER INFO =================
user_email = st.session_state.current_user
user = st.session_state.users[user_email]

st.sidebar.success(f"Logged in as {user['role']}")
st.sidebar.write(user_email)

if st.sidebar.button("Logout"):
    logout()
    st.rerun()

# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🅿️ Parking", "🎉 Events", "👤 Profile", "📊 Dashboard"]
)

# ================= PARKING =================
if page == "🅿️ Parking":

    st.title("🅿️ Parking System")

    vehicle = st.text_input("Vehicle Number")

    zone = "Zone A (Faculty)" if user["role"] == "Faculty" else "Zone B (Student)"

    if st.button("Book Parking"):

        pid = "PSMART+" + hashlib.md5(
            (vehicle + str(datetime.now())).encode()
        ).hexdigest()[:10].upper()

        st.session_state.bookings.append({
            "User": user_email,
            "Vehicle": vehicle,
            "Zone": zone,
            "Time": str(datetime.now())
        })

        qr = make_qr(pid)

        st.success("Booked Successfully")
        st.image(qr)
        st.code(pid)


# ================= EVENTS =================
elif page == "🎉 Events":

    st.title("🎉 Event Parking")

    event = st.selectbox("Event", ["Tech Fest", "Convocation"])
    vehicle = st.text_input("Vehicle")

    if st.button("Book Event"):

        pid = "EVENT+" + hashlib.md5(
            (vehicle + event + str(datetime.now())).encode()
        ).hexdigest()[:10].upper()

        st.session_state.event_bookings.append({
            "User": user_email,
            "Event": event,
            "Vehicle": vehicle,
            "Time": str(datetime.now())
        })

        qr = make_qr(pid)

        st.success("Event Booked")
        st.image(qr)
        st.code(pid)


# ================= PROFILE =================
elif page == "👤 Profile":

    st.title("👤 Profile")

    st.write("Name:", user["name"])
    st.write("Email:", user_email)
    st.write("Role:", user["role"])

    st.subheader("🔐 Change Password")

    old = st.text_input("Old Password", type="password")
    new = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        msg = change_password(user_email, old, new)
        if msg == "Password updated":
            st.success(msg)
        else:
            st.error(msg)


# ================= DASHBOARD =================
elif page == "📊 Dashboard":

    st.title("📊 Dashboard")

    st.metric("Total Bookings", len(st.session_state.bookings))
    st.metric("Event Bookings", len(st.session_state.event_bookings))

    st.subheader("Recent Parking")
    st.dataframe(pd.DataFrame(st.session_state.bookings))

    st.subheader("Event Data")
    st.dataframe(pd.DataFrame(st.session_state.event_bookings))