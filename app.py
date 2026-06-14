import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO
import pandas as pd

# ================= DB SETUP =================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    name TEXT,
    password TEXT,
    role TEXT
)
""")
conn.commit()

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ParkSmart", layout="wide", page_icon="🚗")


# ================= STYLE (CLEAN LOGIN UI) =================
def login_ui():

    st.markdown("""
    <style>

    .login-box {
        max-width: 400px;
        margin: auto;
        padding: 35px;
        background: #111827;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.4);
        text-align: center;
    }

    .title {
        font-size: 26px;
        font-weight: bold;
        color: #60a5fa;
    }

    .sub {
        color: #9ca3af;
        margin-bottom: 20px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: #2563eb;
        color: white;
        font-weight: bold;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>🏫 ParkSmart Login</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Mahindra University Smart Parking</div>", unsafe_allow_html=True)

    email = st.text_input("University Email")
    name = st.text_input("Full Name (only for new users)")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):

            c.execute("SELECT * FROM users WHERE email=?", (email,))
            user = c.fetchone()

            if user:
                if user[2] == password:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Wrong password")
            else:
                st.error("User not found. Please register first.")

    with col2:
        if st.button("Register"):

            role = "Student" if email[:2].isdigit() else "Faculty"

            c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?)",
                      (email, name, password, role))
            conn.commit()

            st.success("Registered Successfully! Now login.")

    st.markdown("</div>", unsafe_allow_html=True)


# ================= INIT =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_ui()
    st.stop()


# ================= USER =================
user_email, user_name, user_pass, role = st.session_state.user

st.sidebar.success(f"{role}")
st.sidebar.write(user_email)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()


# ================= DATA =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "events" not in st.session_state:
    st.session_state.events = [
        {"name": "Tech Fest", "slots": 50, "booked": 0},
        {"name": "Convocation", "slots": 80, "booked": 0}
    ]


# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf


# ================= NAV =================
page = st.sidebar.radio(
    "Navigation",
    ["🅿️ Parking", "🎉 Events", "📊 Dashboard"]
)


# ======================================================
# 🅿️ PARKING
# ======================================================
if page == "🅿️ Parking":

    st.title("🅿️ Parking System")

    vehicle = st.text_input("Vehicle Number")

    zone = "Zone A (Faculty)" if role == "Faculty" else "Zone B (Student)"

    if st.button("Book Parking"):

        pid = hashlib.md5((vehicle + str(datetime.now())).encode()).hexdigest()[:10]

        st.session_state.bookings.append({
            "User": user_email,
            "Vehicle": vehicle,
            "Zone": zone,
            "Time": str(datetime.now())
        })

        st.image(make_qr(pid))
        st.success("Booked Successfully")
        st.code(pid)


# ======================================================
# 🎉 EVENTS
# ======================================================
elif page == "🎉 Events":

    st.title("🎉 Event Parking")

    event = st.selectbox("Event", [e["name"] for e in st.session_state.events])
    vehicle = st.text_input("Vehicle")

    if st.button("Book Event"):

        pid = hashlib.md5((vehicle + event + str(datetime.now())).encode()).hexdigest()[:10]

        st.session_state.bookings.append({
            "User": user_email,
            "Vehicle": vehicle,
            "Zone": f"Event-{event}",
            "Time": str(datetime.now())
        })

        st.image(make_qr(pid))
        st.success("Event Booked")
        st.code(pid)


# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":

    st.title("📊 Dashboard")

    st.metric("Total Bookings", len(st.session_state.bookings))

    st.dataframe(pd.DataFrame(st.session_state.bookings))