import streamlit as st
import random
import hashlib
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Smart Campus Parking System",
    page_icon="🚗",
    layout="wide"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
.main { background-color: #0b1220; color: #e5e7eb; }

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

div[data-testid="metric-container"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #1f2937;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}

h1, h2, h3 { color: #60a5fa; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "history" not in st.session_state:
    st.session_state.history = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

if "event_mode" not in st.session_state:
    st.session_state.event_mode = False

# ---------------- DATA ENGINE ----------------
TOTAL = 500

def ai(hour):
    base = 180
    trend = (hour - 8) * 30
    noise = random.randint(-5, 5)
    mult = 1.4 if st.session_state.event_mode else 1.0
    return int((base + trend + noise) * mult)

zones = {
    "Zone A": random.randint(60, 95),
    "Zone B": random.randint(40, 90),
    "Zone C": random.randint(30, 85),
    "Zone D": random.randint(20, 75),
}

# ---------------- NAVIGATION ----------------
st.sidebar.title("🚗 Parking System")

page = st.sidebar.radio(
    "Menu",
    ["Dashboard", "AI Engine", "Live Zones", "Smart Booking", "My Pass", "History"]
)

st.session_state.event_mode = st.sidebar.toggle("🎯 Event Mode")

# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("🏢 Campus Dashboard")

    hour = datetime.now().hour
    predicted = ai(hour)

    occupied = min(predicted, TOTAL)
    available = TOTAL - occupied

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Slots", TOTAL)
    col2.metric("Occupied", occupied)
    col3.metric("Available", available)
    col4.metric("Occupancy %", f"{round((occupied/TOTAL)*100,2)}%")

    st.info(f"Peak Zone → {max(zones, key=zones.get)}")
    st.success(f"Best Time → {random.randint(8,10)}:{random.choice(['00','30'])} AM")

# ---------------- AI ENGINE ----------------
elif page == "AI Engine":

    st.title("🧠 AI Prediction")

    hour = st.slider("Hour", 8, 20, 10)

    pred = ai(hour)
    risk = min(100, pred // 5)

    st.metric("Predicted Occupancy", pred)

    if risk > 75:
        st.error("High Congestion")
    elif risk > 45:
        st.warning("Medium Congestion")
    else:
        st.success("Low Congestion")

    st.info(f"Recommended Zone → {min(zones, key=zones.get)}")

# ---------------- LIVE ZONES ----------------
elif page == "Live Zones":

    st.title("📡 Live Zones")

    for z, v in zones.items():
        if v > 80:
            st.error(f"{z} → {v}% FULL")
        elif v > 50:
            st.warning(f"{z} → {v}% BUSY")
        else:
            st.success(f"{z} → {v}% FREE")

# ---------------- SMART BOOKING ----------------
elif page == "Smart Booking":

    st.title("🚗 Smart Booking System")

    vehicle = st.text_input("Vehicle Number")
    user = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])

    recommended = min(zones, key=zones.get)

    st.info(f"AI Suggests → {recommended}")

    if st.button("Generate Pass"):

        if not vehicle:
            st.error("Enter vehicle number")

        else:
            slot = random.choice([True, True, False])

            if slot:

                raw = vehicle + str(datetime.now())
                pass_id = "PASS-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

                st.success("Booking Confirmed")
                st.code(pass_id)

                st.session_state.pass_id = pass_id
                st.session_state.history.append(pass_id)

                st.balloons()

            else:
                wl = "WL-" + str(random.randint(1000,9999))
                st.warning("No slots → Waitlisted")
                st.session_state.waitlist.append(wl)

# ---------------- MY PASS ----------------
elif page == "My Pass":

    st.title("🎫 Active Pass")

    if st.session_state.pass_id:
        st.success(st.session_state.pass_id)

        if st.button("Cancel Pass"):
            st.session_state.pass_id = None
            st.warning("Cancelled")

    else:
        st.info("No active pass")

# ---------------- HISTORY ----------------
elif page == "History":

    st.title("📊 System History")

    st.write("Bookings:")
    st.write(st.session_state.history)

    st.write("Waitlist:")
    st.write(st.session_state.waitlist)